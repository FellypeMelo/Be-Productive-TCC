package content

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
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

// Service handles content business logic
type Service struct {
	repo           Repository
	recommenderURL string
	httpClient     *http.Client
}

// NewService creates a new content service
func NewService(repo Repository, recommenderURL string) *Service {
	return &Service{
		repo:           repo,
		recommenderURL: recommenderURL,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
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
func (s *Service) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int, absoluteModeActive bool, declaredGoal string) ([]domain.Content, string, error) {
	// 1. Try to get recommendations from external service
	contentIDs, scores, frictionLevel, err := s.fetchRecommendations(ctx, userID, category, topicID, limit, absoluteModeActive, declaredGoal)
	if err != nil || len(contentIDs) == 0 {
		// Fallback: simple DB-only feed if recommender fails or returns nothing (KISS/Resilience)
		fmt.Printf("Warning: Recommender failed or returned no data: %v. Falling back to DB feed.\n", err)
		contents, dbErr := s.repo.GetFeed(ctx, userID, category, topicID, limit)
		return contents, "none", dbErr
	}

	fmt.Printf("Success: Received %d recommendations from service for user %d (Topic: %d). Friction: %s\n", len(contentIDs), userID, topicID, frictionLevel)
	// 2. Fetch content details from Repository using Batch Get
	contents, err := s.repo.GetByIDs(ctx, contentIDs)
	if err != nil {
		fmt.Printf("Warning: Failed to fetch content details for recommended IDs: %v. Falling back.\n", err)
		contents, _ = s.repo.GetFeed(ctx, userID, category, topicID, limit)
	}

	// 3. Update quality scores from recommender
	s.updateContentScores(ctx, contentIDs, scores)

	return contents, frictionLevel, nil
}

func (s *Service) updateContentScores(ctx context.Context, contentIDs []int64, scores []float64) {
	if len(contentIDs) != len(scores) {
		return
	}
	for i, id := range contentIDs {
		_ = s.repo.UpdateQualityScore(ctx, id, scores[i])
	}
}

func (s *Service) fetchRecommendations(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int, absoluteModeActive bool, declaredGoal string) ([]int64, []float64, string, error) {
	url := fmt.Sprintf("%s/api/v1/recommend", s.recommenderURL)

	params := map[string]interface{}{
		"user_id":              userID,
		"limit":                limit,
		"absolute_mode_active": absoluteModeActive,
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
		return nil, nil, "none", err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return nil, nil, "none", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, nil, "none", fmt.Errorf("recommender returned status %d", resp.StatusCode)
	}

	var result struct {
		ContentIDs    []int64   `json:"content_ids"`
		Scores        []float64 `json:"scores"`
		FrictionLevel string    `json:"friction_level"`
		ModelVersion  string    `json:"model_version"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, nil, "none", err
	}

	return result.ContentIDs, result.Scores, result.FrictionLevel, nil
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
