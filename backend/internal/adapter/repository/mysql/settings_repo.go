package mysql

import (
	"context"
	"database/sql"

	"github.com/be-productive/backend/internal/domain"
)

type SettingsRepository struct {
	db *sql.DB
}

func NewSettingsRepository(db *sql.DB) *SettingsRepository {
	return &SettingsRepository{db: db}
}

func (r *SettingsRepository) GetByUserID(ctx context.Context, userID int64) (*domain.UserSettings, error) {
	query := `
		SELECT id_usuario, sugestao_saudavel_ativa, personalizacao_ativa, notificacao_foco_ativa
		FROM usuario_configuracao WHERE id_usuario = ?
	`
	settings := &domain.UserSettings{}
	err := r.db.QueryRowContext(ctx, query, userID).Scan(
		&settings.UsuarioID, &settings.SugestaoSaudavelAtiva,
		&settings.PersonalizacaoAtiva, &settings.NotificacaoFocoAtiva)

	if err == sql.ErrNoRows {
		// Return default settings if none found (KISS)
		return &domain.UserSettings{
			UsuarioID:             userID,
			SugestaoSaudavelAtiva: true,
			PersonalizacaoAtiva:   true,
			NotificacaoFocoAtiva:  true,
		}, nil
	}
	if err != nil {
		return nil, err
	}
	return settings, nil
}

func (r *SettingsRepository) Update(ctx context.Context, settings *domain.UserSettings) error {
	query := `
		INSERT INTO usuario_configuracao (id_usuario, sugestao_saudavel_ativa, personalizacao_ativa, notificacao_foco_ativa)
		VALUES (?, ?, ?, ?)
		ON DUPLICATE KEY UPDATE 
			sugestao_saudavel_ativa = VALUES(sugestao_saudavel_ativa),
			personalizacao_ativa = VALUES(personalizacao_ativa),
			notificacao_foco_ativa = VALUES(notificacao_foco_ativa)
	`
	_, err := r.db.ExecContext(ctx, query,
		settings.UsuarioID, settings.SugestaoSaudavelAtiva,
		settings.PersonalizacaoAtiva, settings.NotificacaoFocoAtiva)
	return err
}
