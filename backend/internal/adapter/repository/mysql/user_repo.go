package mysql

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/be-productive/backend/internal/domain"
)

// UserRepository implements user.Repository
type UserRepository struct {
	db *sql.DB
}

// NewUserRepository creates a new user repository
func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

// Create inserts a new user
func (r *UserRepository) Create(ctx context.Context, user *domain.User) error {
	query := `
		INSERT INTO usuario (nome, email, senha_criptografada, estado_emocional_inferido)
		VALUES (?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query,
		user.Nome, user.Email, user.SenhaCriptografada, user.EstadoEmocionalInferido)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	user.ID = id
	return nil
}

// GetByID retrieves a user by ID
func (r *UserRepository) GetByID(ctx context.Context, id int64) (*domain.User, error) {
	query := `
		SELECT id_usuario, nome, email, senha_criptografada, estado_emocional_inferido
		FROM usuario WHERE id_usuario = ?
	`
	user := &domain.User{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&user.ID, &user.Nome, &user.Email, &user.SenhaCriptografada, &user.EstadoEmocionalInferido)
	if err == sql.ErrNoRows {
		return nil, domain.ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return user, nil
}

// GetByEmail retrieves a user by email
func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
	query := `
		SELECT id_usuario, nome, email, senha_criptografada, estado_emocional_inferido
		FROM usuario WHERE email = ?
	`
	user := &domain.User{}
	err := r.db.QueryRowContext(ctx, query, email).Scan(
		&user.ID, &user.Nome, &user.Email, &user.SenhaCriptografada, &user.EstadoEmocionalInferido)
	if err == sql.ErrNoRows {
		return nil, domain.ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return user, nil
}

// Update modifies a user
func (r *UserRepository) Update(ctx context.Context, user *domain.User) error {
	query := `
		UPDATE usuario SET nome = ?, estado_emocional_inferido = ?
		WHERE id_usuario = ?
	`
	_, err := r.db.ExecContext(ctx, query, user.Nome, user.EstadoEmocionalInferido, user.ID)
	return err
}

// AddTopics associates topics with a user
func (r *UserRepository) AddTopics(ctx context.Context, userID int64, topicIDs []int64) error {
	// First, remove existing topics
	_, err := r.db.ExecContext(ctx, "DELETE FROM usuario_topico WHERE id_usuario = ?", userID)
	if err != nil {
		return err
	}

	// Insert new topics
	query := "INSERT INTO usuario_topico (id_usuario, id_topico) VALUES (?, ?)"
	for _, topicID := range topicIDs {
		_, err := r.db.ExecContext(ctx, query, userID, topicID)
		if err != nil {
			return err
		}
	}
	return nil
}

// GetTopics retrieves user's topics
func (r *UserRepository) GetTopics(ctx context.Context, userID int64) ([]domain.Topic, error) {
	query := `
		SELECT t.id_topico, t.nome_topico, t.descricao
		FROM topico t
		INNER JOIN usuario_topico ut ON t.id_topico = ut.id_topico
		WHERE ut.id_usuario = ?
	`
	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	topics := []domain.Topic{}
	for rows.Next() {
		var topic domain.Topic
		if err := rows.Scan(&topic.ID, &topic.NomeTopico, &topic.Descricao); err != nil {
			return nil, err
		}
		topics = append(topics, topic)
	}
	return topics, nil
}

// GetSettings retrieves user configuration (UC17)
func (r *UserRepository) GetSettings(ctx context.Context, userID int64) (*domain.UserSettings, error) {
	query := `
		SELECT id_usuario, sugestao_saudavel_ativa, personalizacao_ativa,
		       notificacao_foco_ativa, consentimento_pesquisa, consentimento_pesquisa_versao
		FROM usuario_configuracao WHERE id_usuario = ?
	`
	settings := &domain.UserSettings{}
	err := r.db.QueryRowContext(ctx, query, userID).Scan(
		&settings.UsuarioID, &settings.SugestaoSaudavelAtiva,
		&settings.PersonalizacaoAtiva, &settings.NotificacaoFocoAtiva,
		&settings.PesquisaConsentimento, &settings.PesquisaConsentimentoVersao)

	if err == sql.ErrNoRows {
		return &domain.UserSettings{
			UsuarioID:             userID,
			SugestaoSaudavelAtiva: true,
			PersonalizacaoAtiva:   true,
			NotificacaoFocoAtiva:  true,
			PesquisaConsentimento: false,
		}, nil
	}
	if err != nil {
		return nil, err
	}
	return settings, nil
}

// UpdateSettings updates user configuration (UC17)
func (r *UserRepository) UpdateSettings(ctx context.Context, settings *domain.UserSettings) error {
	query := `
		INSERT INTO usuario_configuracao
			(id_usuario, sugestao_saudavel_ativa, personalizacao_ativa,
			 notificacao_foco_ativa, consentimento_pesquisa, consentimento_pesquisa_versao)
		VALUES (?, ?, ?, ?, ?, ?)
		ON DUPLICATE KEY UPDATE 
			sugestao_saudavel_ativa = VALUES(sugestao_saudavel_ativa),
			personalizacao_ativa = VALUES(personalizacao_ativa),
			notificacao_foco_ativa = VALUES(notificacao_foco_ativa),
			consentimento_pesquisa = VALUES(consentimento_pesquisa),
			consentimento_pesquisa_versao = VALUES(consentimento_pesquisa_versao)
	`
	_, err := r.db.ExecContext(ctx, query,
		settings.UsuarioID, settings.SugestaoSaudavelAtiva,
		settings.PersonalizacaoAtiva, settings.NotificacaoFocoAtiva,
		settings.PesquisaConsentimento, settings.PesquisaConsentimentoVersao)
	return err
}

// GetInactiveUsers finds users who hasn't been active (updated_at) since threshold (UC18)
func (r *UserRepository) GetInactiveUsers(ctx context.Context, threshold time.Time) ([]domain.User, error) {
	query := `
		SELECT id_usuario, nome, email, estado_emocional_inferido 
		FROM usuario WHERE updated_at < ?
	`
	rows, err := r.db.QueryContext(ctx, query, threshold)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	users := []domain.User{}
	for rows.Next() {
		var u domain.User
		if err := rows.Scan(&u.ID, &u.Nome, &u.Email, &u.EstadoEmocionalInferido); err != nil {
			return nil, err
		}
		users = append(users, u)
	}
	return users, nil
}

// AnonimizeUser scrubs personal data while keeping the record for integrity (UC18)
func (r *UserRepository) AnonimizeUser(ctx context.Context, userID int64) error {
	anonEmail := fmt.Sprintf("anon_%d@be-productive.internal", userID)
	query := `
		UPDATE usuario 
		SET nome = 'Anonymous User', 
		    email = ?, 
		    senha_criptografada = 'SCRUBBED',
		    estado_emocional_inferido = 'NEUTRO'
		WHERE id_usuario = ?
	`
	_, err := r.db.ExecContext(ctx, query, anonEmail, userID)
	return err
}
