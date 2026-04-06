package focus

import (
	"context"
	"testing"
	"time"

	"github.com/be-productive/backend/internal/domain"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type mockFocusRepo struct {
	goals            map[int64]*domain.FocusGoal
	sessions         map[int64]*domain.Session
	sessionGoals     map[int64][]domain.FocusGoal
	goalIDCounter    int64
	sessionIDCounter int64
}

func newMockFocusRepo() *mockFocusRepo {
	return &mockFocusRepo{
		goals:        make(map[int64]*domain.FocusGoal),
		sessions:     make(map[int64]*domain.Session),
		sessionGoals: make(map[int64][]domain.FocusGoal),
	}
}

func (m *mockFocusRepo) CreateGoal(ctx context.Context, goal *domain.FocusGoal) error {
	m.goalIDCounter++
	goal.ID = m.goalIDCounter
	m.goals[goal.ID] = goal
	return nil
}
func (m *mockFocusRepo) GetGoalByID(ctx context.Context, id int64) (*domain.FocusGoal, error) {
	if g, ok := m.goals[id]; ok {
		return g, nil
	}
	return nil, domain.ErrNotFound
}
func (m *mockFocusRepo) ListGoals(ctx context.Context, userID int64) ([]domain.FocusGoal, error) {
	var results []domain.FocusGoal
	for _, g := range m.goals {
		if g.UsuarioAssociadoID == userID {
			results = append(results, *g)
		}
	}
	return results, nil
}
func (m *mockFocusRepo) UpdateGoal(ctx context.Context, goal *domain.FocusGoal) error {
	m.goals[goal.ID] = goal
	return nil
}
func (m *mockFocusRepo) CreateSession(ctx context.Context, session *domain.Session) error {
	m.sessionIDCounter++
	session.ID = m.sessionIDCounter
	m.sessions[session.ID] = session
	return nil
}
func (m *mockFocusRepo) GetSessionByID(ctx context.Context, id int64) (*domain.Session, error) {
	if s, ok := m.sessions[id]; ok {
		return s, nil
	}
	return nil, domain.ErrNotFound
}
func (m *mockFocusRepo) ListSessions(ctx context.Context, userID int64, activeOnly bool) ([]domain.Session, error) {
	var results []domain.Session
	for _, s := range m.sessions {
		if s.UsuarioAssociadoID == userID {
			results = append(results, *s)
		}
	}
	return results, nil
}
func (m *mockFocusRepo) UpdateSession(ctx context.Context, session *domain.Session) error {
	m.sessions[session.ID] = session
	return nil
}
func (m *mockFocusRepo) LinkSessionGoals(ctx context.Context, sessionID int64, goalIDs []int64) error {
	for _, gid := range goalIDs {
		if g, ok := m.goals[gid]; ok {
			m.sessionGoals[sessionID] = append(m.sessionGoals[sessionID], *g)
		}
	}
	return nil
}
func (m *mockFocusRepo) GetSessionGoals(ctx context.Context, sessionID int64) ([]domain.FocusGoal, error) {
	return m.sessionGoals[sessionID], nil
}

func TestCreateGoalCreatesBothCategories(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, err := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID:              1,
		TempoProdutividade:  30,
		TempoEntretenimento: 15,
		ModoAbsoluto:        false,
	})

	require.NoError(t, err)
	assert.Equal(t, 2, len(goals))
	assert.Equal(t, domain.CategoryProdutividade, goals[0].Categoria)
	assert.Equal(t, domain.CategoryEntretenimento, goals[1].Categoria)
	assert.Equal(t, domain.FocusGoalStatusAtiva, goals[0].Status)
}

func TestCreateGoalOnlyProductivity(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, err := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID:              1,
		TempoProdutividade:  45,
		TempoEntretenimento: 0,
	})

	require.NoError(t, err)
	assert.Equal(t, 1, len(goals))
	assert.Equal(t, 45, goals[0].DuracaoDefinida)
}

func TestCreateGoalOnlyEntertainment(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, err := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID:              1,
		TempoProdutividade:  0,
		TempoEntretenimento: 20,
	})

	require.NoError(t, err)
	assert.Equal(t, 1, len(goals))
	assert.Equal(t, domain.CategoryEntretenimento, goals[0].Categoria)
}

func TestStartSessionLinksGoals(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	input := CreateGoalInput{UserID: 1, TempoProdutividade: 25, TempoEntretenimento: 10}
	goals, _ := svc.CreateGoal(context.Background(), input)
	goalIDs := []int64{goals[0].ID}
	if len(goals) > 1 {
		goalIDs = append(goalIDs, goals[1].ID)
	}

	session, err := svc.StartSession(context.Background(), 1, goalIDs, true)

	require.NoError(t, err)
	assert.True(t, session.ModoAbsoluto)

	sessionGoals, _ := svc.GetSessionGoals(context.Background(), session.ID)
	assert.Equal(t, len(goalIDs), len(sessionGoals))
}

func TestEndSessionUpdatesFields(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 30, TempoEntretenimento: 15,
	})

	session, _ := svc.StartSession(context.Background(), 1, []int64{goals[0].ID}, false)

	fb := 4
	ended, err := svc.EndSession(context.Background(), session.ID, EndSessionInput{
		TempoProdutividadeRealizado:  28,
		TempoEntretenimentoRealizado: 14,
		Feedback:                     &fb,
	})

	require.NoError(t, err)
	assert.Equal(t, 28, ended.TempoProdutividadeRealizado)
	assert.Equal(t, 14, ended.TempoEntretenimentoRealizado)
	assert.NotNil(t, ended.FeedbackDaSessao)
	assert.Equal(t, 4, *ended.FeedbackDaSessao)
}

func TestEndSessionMarksGoalsCompleted(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 30, TempoEntretenimento: 15,
	})
	goalIDs := []int64{goals[0].ID}
	if len(goals) > 1 {
		goalIDs = append(goalIDs, goals[1].ID)
	}

	session, _ := svc.StartSession(context.Background(), 1, goalIDs, false)

	svc.EndSession(context.Background(), session.ID, EndSessionInput{
		TempoProdutividadeRealizado:  30,
		TempoEntretenimentoRealizado: 15,
		Feedback:                     nil,
	})

	// Check the updated goals in the repo (service updates by pointer reference)
	for _, g := range repo.goals {
		if g.UsuarioAssociadoID == 1 {
			assert.Equal(t, domain.FocusGoalStatusConcluida, g.Status)
		}
	}
}

func TestGetReportConcluido(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 30, TempoEntretenimento: 15,
	})
	goalIDs := []int64{goals[0].ID, goals[1].ID}
	session, _ := svc.StartSession(context.Background(), 1, goalIDs, false)

	fb := 5
	svc.EndSession(context.Background(), session.ID, EndSessionInput{
		TempoProdutividadeRealizado:  30,
		TempoEntretenimentoRealizado: 15,
		Feedback:                     &fb,
	})

	report, err := svc.GetReport(context.Background(), session.ID)
	require.NoError(t, err)
	assert.Equal(t, "concluido", report.Classification)
}

func TestGetReportProgresso(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 30, TempoEntretenimento: 0,
	})
	session, _ := svc.StartSession(context.Background(), 1, []int64{goals[0].ID}, false)

	svc.EndSession(context.Background(), session.ID, EndSessionInput{
		TempoProdutividadeRealizado:  20, // 20 >= 30/2 = 15 → progresso
		TempoEntretenimentoRealizado: 0,
		Feedback:                     nil,
	})

	report, err := svc.GetReport(context.Background(), session.ID)
	require.NoError(t, err)
	assert.Equal(t, "progresso", report.Classification)
}

func TestGetReportNaoConcluido(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 30, TempoEntretenimento: 0,
	})
	session, _ := svc.StartSession(context.Background(), 1, []int64{goals[0].ID}, false)

	svc.EndSession(context.Background(), session.ID, EndSessionInput{
		TempoProdutividadeRealizado:  5, // 5 < 30/2 = 15 → nao_concluido
		TempoEntretenimentoRealizado: 0,
		Feedback:                     nil,
	})

	report, err := svc.GetReport(context.Background(), session.ID)
	require.NoError(t, err)
	assert.Equal(t, "nao_concluido", report.Classification)
}

func TestGetReportCompromissoPerdidoAbsoluteMode(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 30, TempoEntretenimento: 0,
	})
	session, _ := svc.StartSession(context.Background(), 1, []int64{goals[0].ID}, true) // absolute mode

	svc.EndSession(context.Background(), session.ID, EndSessionInput{
		TempoProdutividadeRealizado:  20, // < 30 planned, absolute mode → compromisso_perdido
		TempoEntretenimentoRealizado: 0,
		Feedback:                     nil,
	})

	report, err := svc.GetReport(context.Background(), session.ID)
	require.NoError(t, err)
	assert.Equal(t, "compromisso_perdido", report.Classification)
}

func TestGetReportCompromissoPerdidoNeverStarted(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	session := &domain.Session{UsuarioAssociadoID: 1, HoraInicio: time.Now(), ModoAbsoluto: false}
	repo.CreateSession(context.Background(), session)

	report, err := svc.GetReport(context.Background(), session.ID)
	require.NoError(t, err)
	assert.Equal(t, "compromisso_perdido", report.Classification)
	assert.Contains(t, report.Message, "não foi iniciada")
}

func TestListGoalsForUser(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 25,
	})
	svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 2, TempoEntretenimento: 15,
	})

	user1Goals, _ := svc.ListGoals(context.Background(), 1)
	assert.Equal(t, 1, len(user1Goals))
	assert.Equal(t, int64(1), user1Goals[0].UsuarioAssociadoID)
}

func TestListSessionsForUser(t *testing.T) {
	repo := newMockFocusRepo()
	svc := NewService(repo)

	goals, _ := svc.CreateGoal(context.Background(), CreateGoalInput{
		UserID: 1, TempoProdutividade: 25,
	})
	svc.StartSession(context.Background(), 1, []int64{goals[0].ID}, false)

	sessions, _ := svc.ListSessions(context.Background(), 1, false)
	assert.Equal(t, 1, len(sessions))
}
