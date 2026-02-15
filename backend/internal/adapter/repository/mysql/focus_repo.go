package mysql

import (
	"context"
	"database/sql"

	"github.com/be-productive/backend/internal/domain"
)

// FocusRepository implements focus.Repository
type FocusRepository struct {
	db *sql.DB
}

// NewFocusRepository creates a new focus repository
func NewFocusRepository(db *sql.DB) *FocusRepository {
	return &FocusRepository{db: db}
}

// CreateGoal inserts a new focus goal
func (r *FocusRepository) CreateGoal(ctx context.Context, goal *domain.FocusGoal) error {
	query := `
		INSERT INTO meta_de_foco (usuario_associado_id, categoria, duracao_definida, status)
		VALUES (?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query,
		goal.UsuarioAssociadoID, goal.Categoria, goal.DuracaoDefinida, goal.Status)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	goal.ID = id
	return nil
}

// GetGoalByID retrieves a goal by ID
func (r *FocusRepository) GetGoalByID(ctx context.Context, id int64) (*domain.FocusGoal, error) {
	query := `
		SELECT id_meta, usuario_associado_id, categoria, duracao_definida, status
		FROM meta_de_foco WHERE id_meta = ?
	`
	goal := &domain.FocusGoal{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&goal.ID, &goal.UsuarioAssociadoID, &goal.Categoria, &goal.DuracaoDefinida, &goal.Status)
	if err == sql.ErrNoRows {
		return nil, domain.ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return goal, nil
}

// ListGoals retrieves user's goals
func (r *FocusRepository) ListGoals(ctx context.Context, userID int64) ([]domain.FocusGoal, error) {
	query := `
		SELECT id_meta, usuario_associado_id, categoria, duracao_definida, status
		FROM meta_de_foco WHERE usuario_associado_id = ?
		ORDER BY id_meta DESC
	`
	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	goals := []domain.FocusGoal{}
	for rows.Next() {
		var g domain.FocusGoal
		if err := rows.Scan(&g.ID, &g.UsuarioAssociadoID, &g.Categoria, &g.DuracaoDefinida, &g.Status); err != nil {
			return nil, err
		}
		goals = append(goals, g)
	}
	return goals, nil
}

// UpdateGoal updates a goal
func (r *FocusRepository) UpdateGoal(ctx context.Context, goal *domain.FocusGoal) error {
	query := "UPDATE meta_de_foco SET status = ? WHERE id_meta = ?"
	_, err := r.db.ExecContext(ctx, query, goal.Status, goal.ID)
	return err
}

// CreateSession inserts a new session
func (r *FocusRepository) CreateSession(ctx context.Context, session *domain.Session) error {
	query := `
		INSERT INTO sessao_de_uso (usuario_associado_id, hora_inicio, hora_fim, tempo_produtividade_realizado, tempo_entretenimento_realizado, modo_absoluto)
		VALUES (?, ?, NULL, 0, 0, ?)
	`
	result, err := r.db.ExecContext(ctx, query, session.UsuarioAssociadoID, session.HoraInicio, session.ModoAbsoluto)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	session.ID = id
	return nil
}

// GetSessionByID retrieves a session by ID
func (r *FocusRepository) GetSessionByID(ctx context.Context, id int64) (*domain.Session, error) {
	query := `
		SELECT id_sessao, usuario_associado_id, hora_inicio, hora_fim, 
		       tempo_produtividade_realizado, tempo_entretenimento_realizado, feedback_da_sessao, modo_absoluto
		FROM sessao_de_uso WHERE id_sessao = ?
	`
	session := &domain.Session{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&session.ID, &session.UsuarioAssociadoID, &session.HoraInicio, &session.HoraFim,
		&session.TempoProdutividadeRealizado, &session.TempoEntretenimentoRealizado, &session.FeedbackDaSessao, &session.ModoAbsoluto)
	if err == sql.ErrNoRows {
		return nil, domain.ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return session, nil
}

// ListSessions retrieves user's sessions
func (r *FocusRepository) ListSessions(ctx context.Context, userID int64, activeOnly bool) ([]domain.Session, error) {
	query := `
		SELECT id_sessao, usuario_associado_id, hora_inicio, hora_fim, 
		       tempo_produtividade_realizado, tempo_entretenimento_realizado, feedback_da_sessao, modo_absoluto
		FROM sessao_de_uso WHERE usuario_associado_id = ?
	`
	if activeOnly {
		query += " AND hora_fim IS NULL"
	}
	query += " ORDER BY id_sessao DESC"

	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	sessions := []domain.Session{}
	for rows.Next() {
		var s domain.Session
		if err := rows.Scan(&s.ID, &s.UsuarioAssociadoID, &s.HoraInicio, &s.HoraFim,
			&s.TempoProdutividadeRealizado, &s.TempoEntretenimentoRealizado, &s.FeedbackDaSessao, &s.ModoAbsoluto); err != nil {
			return nil, err
		}
		sessions = append(sessions, s)
	}
	return sessions, nil
}

// UpdateSession updates a session
func (r *FocusRepository) UpdateSession(ctx context.Context, session *domain.Session) error {
	query := `
		UPDATE sessao_de_uso 
		SET hora_fim = ?, tempo_produtividade_realizado = ?, tempo_entretenimento_realizado = ?, feedback_da_sessao = ?, modo_absoluto = ?
		WHERE id_sessao = ?
	`
	_, err := r.db.ExecContext(ctx, query,
		session.HoraFim, session.TempoProdutividadeRealizado, session.TempoEntretenimentoRealizado, session.FeedbackDaSessao, session.ModoAbsoluto, session.ID)
	return err
}

// LinkSessionGoals links goals to a session
func (r *FocusRepository) LinkSessionGoals(ctx context.Context, sessionID int64, goalIDs []int64) error {
	query := "INSERT INTO sessao_meta (id_sessao, id_meta) VALUES (?, ?)"
	for _, goalID := range goalIDs {
		_, err := r.db.ExecContext(ctx, query, sessionID, goalID)
		if err != nil {
			return err
		}
	}
	return nil
}

// GetSessionGoals retrieves goals linked to a session
func (r *FocusRepository) GetSessionGoals(ctx context.Context, sessionID int64) ([]domain.FocusGoal, error) {
	query := `
		SELECT m.id_meta, m.usuario_associado_id, m.categoria, m.duracao_definida, m.status
		FROM meta_de_foco m
		INNER JOIN sessao_meta sm ON m.id_meta = sm.id_meta
		WHERE sm.id_sessao = ?
	`
	rows, err := r.db.QueryContext(ctx, query, sessionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	goals := []domain.FocusGoal{}
	for rows.Next() {
		var g domain.FocusGoal
		if err := rows.Scan(&g.ID, &g.UsuarioAssociadoID, &g.Categoria, &g.DuracaoDefinida, &g.Status); err != nil {
			return nil, err
		}
		goals = append(goals, g)
	}
	return goals, nil
}
