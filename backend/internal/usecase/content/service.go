package content

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/be-productive/backend/internal/domain"
)

// Repository defines the content storage interface
type Repository interface {
	Create(ctx context.Context, content *domain.Content, topicIDs []int64) error
	GetByID(ctx context.Context, id int64) (*domain.Content, error)
	GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error)
	GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error)
	UpdateQualityScore(ctx context.Context, id int64, score float64) error
	AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error
	AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error
}

// CreateContentInput represents content creation parameters
type CreateContentInput struct {
	Titulo      string
	Corpo       string
	TipoDeMidia domain.ContentType
	Categoria   domain.ContentCategory
	AutorID     int64
	TopicIDs    []int64
	Tags        string
}

// FeedResult holds the complete feed payload including model scores.
type FeedResult struct {
	Contents          []domain.Content
	Scores            map[int64]float64
	FrictionLevel     string
	ModelVersion      string
	Experiment        string
	ExperimentID      string
	Variant           string
	AssignmentVersion string
	Eligible          bool
	Explanations      map[int64][]string
	Fallback          bool
}

type InteractionRepository interface {
	AddInteraction(ctx context.Context, event domain.ContentInteraction) error
}

type ExposureRepository interface {
	AddExperimentExposure(ctx context.Context, exposure domain.ExperimentExposure) error
}

// FocusGateway exposes the user's server-side focus state used to enforce the
// Ulysses Pact (Absolute Mode) without trusting client-supplied flags.
type FocusGateway interface {
	// GetActiveAbsoluteGoal reports whether the user currently has an active focus
	// session in absolute mode, and the category of its linked goal (may be empty).
	GetActiveAbsoluteGoal(ctx context.Context, userID int64) (bool, string, error)
}

// Service handles content business logic
type Service struct {
	repo            Repository
	recommenderURL  string
	sharedSecret    string
	focus           FocusGateway
	researchConsent func(context.Context, int64) (bool, error)
	httpClient      *http.Client
}

// Option configures optional Service dependencies.
type Option func(*Service)

// WithSharedSecret sets the X-Internal-Auth secret sent to the recommender.
func WithSharedSecret(secret string) Option {
	return func(s *Service) { s.sharedSecret = secret }
}

// WithFocusGateway wires the focus state provider used to enforce Absolute Mode.
func WithFocusGateway(focus FocusGateway) Option {
	return func(s *Service) { s.focus = focus }
}

// WithResearchConsentReader keeps research eligibility server-owned while
// allowing product personalization to remain independent of research consent.
func WithResearchConsentReader(reader func(context.Context, int64) (bool, error)) Option {
	return func(s *Service) { s.researchConsent = reader }
}

// NewService creates a new content service
func NewService(repo Repository, recommenderURL string, opts ...Option) *Service {
	s := &Service{
		repo:           repo,
		recommenderURL: recommenderURL,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

// Create publishes new content (RF005, RF006)
func (s *Service) Create(ctx context.Context, input CreateContentInput) (*domain.Content, error) {
	content := &domain.Content{
		Titulo:           input.Titulo,
		Corpo:            input.Corpo,
		TipoDeMidia:      input.TipoDeMidia,
		Categoria:        input.Categoria,
		AutorID:          input.AutorID,
		DataPublicacao:   time.Now(),
		TagsRelevantes:   input.Tags,
		ScoreDeQualidade: 0.5, // Initial score (RN002)
	}

	if err := s.repo.Create(ctx, content, input.TopicIDs); err != nil {
		return nil, err
	}

	return content, nil
}

// GetByID retrieves content by ID
func (s *Service) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	return s.repo.GetByID(ctx, id)
}

// GetFeed returns personalized feed (RF011, RF014)
// Optionally accepts absoluteModeActive and declaredGoal to activate the recommender's Absolute Mode filter (Eq.2 + Algorithm 4).
func (s *Service) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int, absoluteModeActive bool, declaredGoal string, protectiveModeActive bool) (*FeedResult, error) {
	// Enforce the Ulysses Pact server-side: an active absolute-mode focus session
	// overrides any client-supplied absolute_mode_active / declared_goal. Client
	// query params remain only as a no-auth fallback for anonymous/testing use.
	if s.focus != nil && userID > 0 {
		if active, goal, ferr := s.focus.GetActiveAbsoluteGoal(ctx, userID); ferr == nil && active {
			absoluteModeActive = true
			if goal != "" {
				declaredGoal = goal
			}
		}
	}

	// 1. Try to get recommendations from external service
	researchConsent := false
	if s.researchConsent != nil {
		if consent, consentErr := s.researchConsent(ctx, userID); consentErr == nil {
			researchConsent = consent
		}
	}
	contentIDs, scores, frictionLevel, modelVersion, experiment, experimentID, variant, assignmentVersion, eligible, explanations, err := s.fetchRecommendations(ctx, userID, category, topicID, limit, absoluteModeActive, declaredGoal, protectiveModeActive, researchConsent)
	if err != nil || len(contentIDs) == 0 {
		if protectiveModeActive {
			// Fail closed: a recommender outage must not silently replace a
			// protected feed with unrestricted database results.
			return &FeedResult{
				Contents:      []domain.Content{},
				Scores:        map[int64]float64{},
				FrictionLevel: "high",
				ModelVersion:  "protective-fallback-v1",
				Experiment:    "protective",
				ExperimentID:  "sustainable-attention-v1",
				Variant:       "not_eligible",
				Explanations:  map[int64][]string{},
				Fallback:      true,
			}, nil
		}
		// Fallback: simple DB-only feed if recommender fails or returns nothing (KISS/Resilience)
		fmt.Printf("Warning: Recommender failed or returned no data: %v. Falling back to DB feed.\n", err)
		contents, dbErr := s.repo.GetFeed(ctx, userID, category, topicID, limit)
		if dbErr != nil {
			return nil, dbErr
		}
		return &FeedResult{
			Contents:      contents,
			Scores:        map[int64]float64{},
			FrictionLevel: "none",
			ModelVersion:  "db-fallback-v1",
			Experiment:    "fallback",
			ExperimentID:  "sustainable-attention-v1",
			Variant:       "not_eligible",
			Explanations:  map[int64][]string{},
			Fallback:      true,
		}, nil
	}

	fmt.Printf("Success: Received %d recommendations from service for user %d (Topic: %d). Friction: %s\n", len(contentIDs), userID, topicID, frictionLevel)
	// 2. Fetch content details from Repository using Batch Get
	contents, err := s.repo.GetByIDs(ctx, contentIDs)
	if err != nil {
		if protectiveModeActive {
			return &FeedResult{
				Contents: []domain.Content{}, Scores: map[int64]float64{},
				FrictionLevel: "high", ModelVersion: "protective-fallback-v1",
				Experiment: "protective", Explanations: map[int64][]string{}, Fallback: true,
			}, nil
		}
		fmt.Printf("Warning: Failed to fetch content details for recommended IDs: %v. Falling back.\n", err)
		contents, _ = s.repo.GetFeed(ctx, userID, category, topicID, limit)
	}

	// Personalized rank scores never overwrite global content quality.
	scoreMap := make(map[int64]float64)
	for i, id := range contentIDs {
		if i < len(scores) {
			scoreMap[id] = scores[i]
		}
	}

	return &FeedResult{
		Contents:          contents,
		Scores:            scoreMap,
		FrictionLevel:     frictionLevel,
		ModelVersion:      modelVersion,
		Experiment:        experiment,
		ExperimentID:      experimentID,
		Variant:           variant,
		AssignmentVersion: assignmentVersion,
		Eligible:          eligible,
		Explanations:      explanations,
	}, nil
}

func (s *Service) updateContentScores(ctx context.Context, contentIDs []int64, scores []float64) {
	if len(contentIDs) != len(scores) {
		return
	}
	for i, id := range contentIDs {
		_ = s.repo.UpdateQualityScore(ctx, id, scores[i])
	}
}

func (s *Service) fetchRecommendations(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int, absoluteModeActive bool, declaredGoal string, protectiveModeActive bool, researchConsent bool) ([]int64, []float64, string, string, string, string, string, string, bool, map[int64][]string, error) {
	url := fmt.Sprintf("%s/api/v1/recommend", s.recommenderURL)

	params := map[string]interface{}{
		"user_id":                userID,
		"limit":                  limit,
		"absolute_mode_active":   absoluteModeActive,
		"protective_mode_active": protectiveModeActive,
		"research_consent":       researchConsent,
	}
	if category != "" {
		params["category"] = category
	}
	if topicID > 0 {
		params["topic_id"] = topicID
	}
	if declaredGoal != "" {
		params["declared_goal"] = declaredGoal
	}

	reqBody, _ := json.Marshal(params)

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, nil, "none", "", "", "", "", "", false, nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if s.sharedSecret != "" {
		req.Header.Set("X-Internal-Auth", s.sharedSecret)
	}

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return nil, nil, "none", "", "", "", "", "", false, nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, nil, "none", "", "", "", "", "", false, nil, fmt.Errorf("recommender returned status %d", resp.StatusCode)
	}

	var result struct {
		ContentIDs        []int64             `json:"content_ids"`
		Scores            []float64           `json:"scores"`
		FrictionLevel     string              `json:"friction_level"`
		ModelVersion      string              `json:"model_version"`
		Experiment        string              `json:"experiment"`
		ExperimentID      string              `json:"experiment_id"`
		Variant           string              `json:"variant"`
		AssignmentVersion string              `json:"assignment_version"`
		Eligible          bool                `json:"eligible"`
		Explanations      map[string][]string `json:"explanations"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, nil, "none", "", "", "", "", "", false, nil, err
	}
	explanations := make(map[int64][]string, len(result.Explanations))
	for rawID, reasons := range result.Explanations {
		if id, parseErr := strconv.ParseInt(rawID, 10, 64); parseErr == nil {
			explanations[id] = reasons
		}
	}
	return result.ContentIDs, result.Scores, result.FrictionLevel, result.ModelVersion, result.Experiment, result.ExperimentID, result.Variant, result.AssignmentVersion, result.Eligible, explanations, nil
}

// RecordExperimentExposure stores only the minimum exposure contract. The
// handler supplies the authenticated user id; no raw scroll or context data is accepted.
func (s *Service) RecordExperimentExposure(ctx context.Context, exposure domain.ExperimentExposure) error {
	if exposure.EventID == "" || len(exposure.EventID) > 64 || exposure.UserID < 1 ||
		exposure.ExperimentID != ExperimentID ||
		exposure.AssignmentVersion != AssignmentVersion ||
		exposure.AlgorithmVersion != AlgorithmVersion ||
		exposure.RequestID == "" || len(exposure.RequestID) > 128 ||
		(exposure.Variant != "control" && exposure.Variant != "treatment") ||
		!exposure.Eligible || exposure.PositionCount < 0 || exposure.PositionCount > 50 {
		return domain.ErrInvalidInput
	}
	if stableVariant(exposure.UserID) != exposure.Variant {
		return domain.ErrInvalidInput
	}
	if s.researchConsent == nil {
		return domain.ErrForbidden
	}
	consent, err := s.researchConsent(ctx, exposure.UserID)
	if err != nil {
		return domain.ErrInternalServer
	}
	if !consent {
		return domain.ErrForbidden
	}
	repo, ok := s.repo.(ExposureRepository)
	if !ok {
		return domain.ErrInternalServer
	}
	exposure.CreatedAt = time.Now().UTC()
	return repo.AddExperimentExposure(ctx, exposure)
}

// RecordInteraction stores consent-safe product events. Raw fatigue telemetry is excluded.
func (s *Service) RecordInteraction(ctx context.Context, event domain.ContentInteraction) error {
	valid := map[string]bool{"impression": true, "open": true, "complete": true, "hide": true}
	if !valid[event.Type] || event.EventID == "" || event.ContentID < 1 || event.UserID < 1 || event.DwellSeconds < 0 || event.Position < 0 {
		return domain.ErrInvalidInput
	}
	if len(event.EventID) > 64 || len(event.Algorithm) > 64 || len(event.Experiment) > 64 {
		return domain.ErrInvalidInput
	}
	// Fatigue state belongs to the edge client. Keep the legacy column neutral
	// even if an older or modified client tries to submit a friction verdict.
	event.FrictionLevel = "none"
	repo, ok := s.repo.(InteractionRepository)
	if !ok {
		return domain.ErrInternalServer
	}
	event.CreatedAt = time.Now().UTC()
	return repo.AddInteraction(ctx, event)
}

// SubmitFeedback records user feedback and updates quality score (RF015, RN002)
func (s *Service) SubmitFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	// Validate feedback type
	validTypes := map[string]bool{
		"util":          true,
		"nao_relevante": true,
		"relaxante":     true,
	}
	if !validTypes[feedbackType] {
		return domain.ErrInvalidInput
	}

	// 1. Get current content to update score (KISS: direct update)
	content, err := s.repo.GetByID(ctx, contentID)
	if err == nil {
		newScore := content.ScoreDeQualidade
		switch feedbackType {
		case "util":
			newScore += 0.05
		case "nao_relevante":
			newScore -= 0.1
		case "relaxante":
			newScore += 0.02
		}

		// Clamp between 0 and 1
		if newScore > 1.0 {
			newScore = 1.0
		}
		if newScore < 0.0 {
			newScore = 0.0
		}

		_ = s.repo.UpdateQualityScore(ctx, contentID, newScore)
	}

	return s.repo.AddFeedback(ctx, contentID, userID, feedbackType)
}

// Report handles content reporting (RF007)
func (s *Service) Report(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	// Validate motivo per RN003
	validMotivos := map[string]bool{
		"desinformacao":    true,
		"discurso_de_odio": true,
		"assedio":          true,
		"violencia":        true,
		"fraude":           true,
		"outro":            true,
	}
	if !validMotivos[motivo] {
		return domain.ErrInvalidInput
	}

	return s.repo.AddReport(ctx, contentID, userID, motivo, detalhes)
}
