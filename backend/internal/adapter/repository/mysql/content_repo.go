package mysql

import (
	"context"
	"database/sql"

	"github.com/be-productive/backend/internal/domain"
)

// ContentRepository implements content.Repository
type ContentRepository struct {
	db *sql.DB
}

// NewContentRepository creates a new content repository
func NewContentRepository(db *sql.DB) *ContentRepository {
	return &ContentRepository{db: db}
}

// Create inserts new content with topic associations
func (r *ContentRepository) Create(ctx context.Context, content *domain.Content, topicIDs []int64) error {
	query := `
		INSERT INTO conteudo (titulo, corpo, midia_url, tipo_de_midia, categoria, autor_id, data_publicacao, tags_relevantes, score_de_qualidade)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query,
		content.Titulo, content.Corpo, content.MidiaURL, content.TipoDeMidia, content.Categoria,
		content.AutorID, content.DataPublicacao, content.TagsRelevantes, content.ScoreDeQualidade)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	content.ID = id

	// Associate topics
	topicQuery := "INSERT INTO conteudo_topico (id_conteudo, id_topico) VALUES (?, ?)"
	for _, topicID := range topicIDs {
		_, err := r.db.ExecContext(ctx, topicQuery, content.ID, topicID)
		if err != nil {
			return err
		}
	}

	return nil
}

// GetByID retrieves content by ID
func (r *ContentRepository) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	query := `
		SELECT id_conteudo, titulo, corpo, COALESCE(midia_url, ''), tipo_de_midia, categoria, autor_id, 
		       COALESCE(data_publicacao, NOW()), COALESCE(tags_relevantes, ''), score_de_qualidade
		FROM conteudo WHERE id_conteudo = ?
	`
	content := &domain.Content{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&content.ID, &content.Titulo, &content.Corpo, &content.MidiaURL, &content.TipoDeMidia,
		&content.Categoria, &content.AutorID, &content.DataPublicacao,
		&content.TagsRelevantes, &content.ScoreDeQualidade)
	if err == sql.ErrNoRows {
		return nil, domain.ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return content, nil
}

// GetByIDs retrieves multiple contents by their IDs
func (r *ContentRepository) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	if len(ids) == 0 {
		return []domain.Content{}, nil
	}

	// Dynamic IN clause building
	query := `
		SELECT id_conteudo, titulo, corpo, COALESCE(midia_url, ''), tipo_de_midia, categoria, autor_id, 
		       COALESCE(data_publicacao, NOW()), COALESCE(tags_relevantes, ''), score_de_qualidade
		FROM conteudo WHERE id_conteudo IN (`

	args := make([]interface{}, len(ids))
	for i, id := range ids {
		query += "?"
		if i < len(ids)-1 {
			query += ","
		}
		args[i] = id
	}
	query += ") ORDER BY FIELD(id_conteudo, "
	for i, id := range ids {
		query += "?"
		if i < len(ids)-1 {
			query += ","
		}
		args = append(args, id)
	}
	query += ")"

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	contents := []domain.Content{}
	for rows.Next() {
		var c domain.Content
		if err := rows.Scan(&c.ID, &c.Titulo, &c.Corpo, &c.MidiaURL, &c.TipoDeMidia,
			&c.Categoria, &c.AutorID, &c.DataPublicacao, &c.TagsRelevantes, &c.ScoreDeQualidade); err != nil {
			return nil, err
		}
		contents = append(contents, c)
	}
	return contents, nil
}

// GetFeed retrieves personalized feed for user
func (r *ContentRepository) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	// Basic feed query - in production, this would integrate with recommender
	query := `
		SELECT c.id_conteudo, c.titulo, c.corpo, COALESCE(c.midia_url, ''), c.tipo_de_midia, c.categoria, 
		       c.autor_id, COALESCE(c.data_publicacao, NOW()), 
		       COALESCE(c.tags_relevantes, ''), c.score_de_qualidade
		FROM conteudo c
		INNER JOIN conteudo_topico ct ON c.id_conteudo = ct.id_conteudo
		INNER JOIN usuario_topico ut ON ct.id_topico = ut.id_topico
		WHERE ut.id_usuario = ?
		  AND (? = '' OR c.categoria = ?)
		  AND (? <= 0 OR ct.id_topico = ?)
		GROUP BY c.id_conteudo
		ORDER BY c.score_de_qualidade DESC, c.data_publicacao DESC
		LIMIT ?
	`
	rows, err := r.db.QueryContext(ctx, query, userID, category, category, topicID, topicID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	contents := []domain.Content{}
	for rows.Next() {
		var c domain.Content
		if err := rows.Scan(&c.ID, &c.Titulo, &c.Corpo, &c.MidiaURL, &c.TipoDeMidia,
			&c.Categoria, &c.AutorID, &c.DataPublicacao, &c.TagsRelevantes, &c.ScoreDeQualidade); err != nil {
			return nil, err
		}
		contents = append(contents, c)
	}
	return contents, nil
}

// UpdateQualityScore updates content quality score
func (r *ContentRepository) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	query := "UPDATE conteudo SET score_de_qualidade = ? WHERE id_conteudo = ?"
	_, err := r.db.ExecContext(ctx, query, score, id)
	return err
}

// AddFeedback records user feedback
func (r *ContentRepository) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	query := `
		INSERT INTO feedback_conteudo (id_conteudo, id_usuario, tipo, created_at)
		VALUES (?, ?, ?, NOW())
	`
	_, err := r.db.ExecContext(ctx, query, contentID, userID, feedbackType)
	return err
}

// AddReport records a content report
func (r *ContentRepository) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	query := `
		INSERT INTO denuncia (id_conteudo, id_usuario, motivo, detalhes, created_at)
		VALUES (?, ?, ?, ?, NOW())
	`
	_, err := r.db.ExecContext(ctx, query, contentID, userID, motivo, detalhes)
	return err
}
