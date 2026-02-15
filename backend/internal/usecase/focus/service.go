package focus

import (
	"context"
	"time"

	"github.com/be-productive/backend/internal/domain"
)

// Repository defines the focus storage interface
type Repository interface {
	CreateGoal(ctx context.Context, goal *domain.FocusGoal) error
	GetGoalByID(ctx context.Context, id int64) (*domain.FocusGoal, error)
	ListGoals(ctx context.Context, userID int64) ([]domain.FocusGoal, error)
	UpdateGoal(ctx context.Context, goal *domain.FocusGoal) error
	
	CreateSession(ctx context.Context, session *domain.Session) error
	GetSessionByID(ctx context.Context, id int64) (*domain.Session, error)
	UpdateSession(ctx context.Context, session *domain.Session) error
	LinkSessionGoals(ctx context.Context, sessionID int64, goalIDs []int64) error
	GetSessionGoals(ctx context.Context, sessionID int64) ([]domain.FocusGoal, error)
}

// CreateGoalInput represents goal creation parameters
type CreateGoalInput struct {
	UserID              int64
	TempoProdutividade  int
	TempoEntretenimento int
	ModoAbsoluto        bool
}

// EndSessionInput represents session end parameters
type EndSessionInput struct {
	TempoProdutividadeRealizado  int
	TempoEntretenimentoRealizado int
	Feedback                     *int
}

// SessionReport represents a session report (RF013)
type SessionReport struct {
	Session        *domain.Session   `json:"session"`
	Goals          []domain.FocusGoal `json:"goals"`
	Classification string             `json:"classification"` // "progresso", "nao_concluido", "compromisso_perdido"
	Message        string             `json:"message"`
}

// Service handles focus business logic
type Service struct {
	repo Repository
}

// NewService creates a new focus service
func NewService(repo Repository) *Service {
	return &Service{repo: repo}
}

// CreateGoal creates focus goals (RF009)
func (s *Service) CreateGoal(ctx context.Context, input CreateGoalInput) ([]domain.FocusGoal, error) {
	var goals []domain.FocusGoal

	if input.TempoProdutividade > 0 {
		goal := &domain.FocusGoal{
			UsuarioAssociadoID: input.UserID,
			Categoria:          domain.CategoryProdutividade,
			DuracaoDefinida:    input.TempoProdutividade,
			Status:             domain.FocusGoalStatusAtiva,
		}
		if err := s.repo.CreateGoal(ctx, goal); err != nil {
			return nil, err
		}
		goals = append(goals, *goal)
	}

	if input.TempoEntretenimento > 0 {
		goal := &domain.FocusGoal{
			UsuarioAssociadoID: input.UserID,
			Categoria:          domain.CategoryEntretenimento,
			DuracaoDefinida:    input.TempoEntretenimento,
			Status:             domain.FocusGoalStatusAtiva,
		}
		if err := s.repo.CreateGoal(ctx, goal); err != nil {
			return nil, err
		}
		goals = append(goals, *goal)
	}

	return goals, nil
}

// ListGoals returns user's focus goals
func (s *Service) ListGoals(ctx context.Context, userID int64) ([]domain.FocusGoal, error) {
	return s.repo.ListGoals(ctx, userID)
}

// StartSession starts a focus session (RF011)
func (s *Service) StartSession(ctx context.Context, userID int64, goalIDs []int64) (*domain.Session, error) {
	session := &domain.Session{
		UsuarioAssociadoID: userID,
		HoraInicio:         time.Now(),
	}

	if err := s.repo.CreateSession(ctx, session); err != nil {
		return nil, err
	}

	if err := s.repo.LinkSessionGoals(ctx, session.ID, goalIDs); err != nil {
		return nil, err
	}

	return session, nil
}

// EndSession ends a focus session
func (s *Service) EndSession(ctx context.Context, sessionID int64, input EndSessionInput) (*domain.Session, error) {
	session, err := s.repo.GetSessionByID(ctx, sessionID)
	if err != nil {
		return nil, err
	}

	session.HoraFim = time.Now()
	session.TempoProdutividadeRealizado = input.TempoProdutividadeRealizado
	session.TempoEntretenimentoRealizado = input.TempoEntretenimentoRealizado
	session.FeedbackDaSessao = input.Feedback

	if err := s.repo.UpdateSession(ctx, session); err != nil {
		return nil, err
	}

	// Update goal statuses
	goals, _ := s.repo.GetSessionGoals(ctx, sessionID)
	for _, goal := range goals {
		goal.Status = domain.FocusGoalStatusConcluida
		s.repo.UpdateGoal(ctx, &goal)
	}

	return session, nil
}

// GetReport generates session report (RF013)
func (s *Service) GetReport(ctx context.Context, sessionID int64) (*SessionReport, error) {
	session, err := s.repo.GetSessionByID(ctx, sessionID)
	if err != nil {
		return nil, err
	}

	goals, err := s.repo.GetSessionGoals(ctx, sessionID)
	if err != nil {
		return nil, err
	}

	report := &SessionReport{
		Session: session,
		Goals:   goals,
	}

	// Calculate classification
	totalPlanned := 0
	totalRealized := session.TempoProdutividadeRealizado + session.TempoEntretenimentoRealizado

	for _, goal := range goals {
		totalPlanned += goal.DuracaoDefinida
	}

	if totalPlanned == 0 {
		report.Classification = "compromisso_perdido"
		report.Message = "A meta não foi iniciada. Que tal tentar novamente?"
	} else if totalRealized >= totalPlanned/2 {
		report.Classification = "progresso"
		report.Message = "Parabéns! Você está fazendo progresso. Continue assim!"
	} else {
		report.Classification = "nao_concluido"
		report.Message = "Você está no caminho certo. Cada pequeno passo conta!"
	}

	return report, nil
}
