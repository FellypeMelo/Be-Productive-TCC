package mysql

import (
	"context"
	"database/sql"

	"github.com/be-productive/backend/internal/domain"
)

type CommunityRepository struct {
	db *sql.DB
}

func NewCommunityRepository(db *sql.DB) *CommunityRepository {
	return &CommunityRepository{db: db}
}

func (r *CommunityRepository) List(ctx context.Context) ([]domain.Community, error) {
	query := "SELECT id_comunidade, nome_comunidade, topico_principal_id, regras_de_moderacao FROM comunidade"
	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	comms := []domain.Community{}
	for rows.Next() {
		var c domain.Community
		if err := rows.Scan(&c.ID, &c.NomeComunidade, &c.TopicoPrincipalID, &c.RegrasDeModeração); err != nil {
			return nil, err
		}
		comms = append(comms, c)
	}
	return comms, nil
}

func (r *CommunityRepository) Join(ctx context.Context, userID, communityID int64) error {
	query := "INSERT IGNORE INTO usuario_comunidade (id_usuario, id_comunidade) VALUES (?, ?)"
	_, err := r.db.ExecContext(ctx, query, userID, communityID)
	return err
}

func (r *CommunityRepository) Leave(ctx context.Context, userID, communityID int64) error {
	query := "DELETE FROM usuario_comunidade WHERE id_usuario = ? AND id_comunidade = ?"
	_, err := r.db.ExecContext(ctx, query, userID, communityID)
	return err
}

func (r *CommunityRepository) GetUserCommunities(ctx context.Context, userID int64) ([]domain.Community, error) {
	query := `
		SELECT c.id_comunidade, c.nome_comunidade, c.topico_principal_id, c.regras_de_moderacao 
		FROM comunidade c
		INNER JOIN usuario_comunidade uc ON c.id_comunidade = uc.id_comunidade
		WHERE uc.id_usuario = ?
	`
	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	comms := []domain.Community{}
	for rows.Next() {
		var c domain.Community
		if err := rows.Scan(&c.ID, &c.NomeComunidade, &c.TopicoPrincipalID, &c.RegrasDeModeração); err != nil {
			return nil, err
		}
		comms = append(comms, c)
	}
	return comms, nil
}
