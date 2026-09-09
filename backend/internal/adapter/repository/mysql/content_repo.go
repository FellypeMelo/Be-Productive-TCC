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

	// Fetch topics
	topics, err := r.fetchTopicsForContents(ctx, []int64{id})
	if err == nil {
		content.Topics = topics[id]
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
	contentIDs := []int64{}
	for rows.Next() {
		var c domain.Content
		if err := rows.Scan(&c.ID, &c.Titulo, &c.Corpo, &c.MidiaURL, &c.TipoDeMidia,
			&c.Categoria, &c.AutorID, &c.DataPublicacao, &c.TagsRelevantes, &c.ScoreDeQualidade); err != nil {
			return nil, err
		}
		contents = append(contents, c)
		contentIDs = append(contentIDs, c.ID)
	}

	// Fetch topics for all contents
	topicsMap, err := r.fetchTopicsForContents(ctx, contentIDs)
	if err == nil {
		for i := range contents {
			contents[i].Topics = topicsMap[contents[i].ID]
		}
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
	contentIDs := []int64{}
	for rows.Next() {
		var c domain.Content
		if err := rows.Scan(&c.ID, &c.Titulo, &c.Corpo, &c.MidiaURL, &c.TipoDeMidia,
			&c.Categoria, &c.AutorID, &c.DataPublicacao, &c.TagsRelevantes, &c.ScoreDeQualidade); err != nil {
			return nil, err
		}
		contents = append(contents, c)
		contentIDs = append(contentIDs, c.ID)
	}

	// Fetch topics for all contents
	topicsMap, err := r.fetchTopicsForContents(ctx, contentIDs)
	if err == nil {
		for i := range contents {
			contents[i].Topics = topicsMap[contents[i].ID]
		}
	}

	return contents, nil
}

func (r *ContentRepository) fetchTopicsForContents(ctx context.Context, contentIDs []int64) (map[int64][]domain.Topic, error) {
	if len(contentIDs) == 0 {
		return make(map[int64][]domain.Topic), nil
	}

	query := `
		SELECT ct.id_conteudo, t.id_topico, t.nome_topico, t.descricao
		FROM topico t
		INNER JOIN conteudo_topico ct ON t.id_topico = ct.id_topico
		WHERE ct.id_conteudo IN (`

	args := make([]interface{}, len(contentIDs))
	for i, id := range contentIDs {
		query += "?"
		if i < len(contentIDs)-1 {
			query += ","
		}
		args[i] = id
	}
	query += ")"

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	topicsMap := make(map[int64][]domain.Topic)
	for rows.Next() {
		var contentID int64
		var t domain.Topic
		if err := rows.Scan(&contentID, &t.ID, &t.NomeTopico, &t.Descricao); err != nil {
			continue
		}
		topicsMap[contentID] = append(topicsMap[contentID], t)
	}

	return topicsMap, nil
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

func (r *ContentRepository) AddInteraction(ctx context.Context, event domain.ContentInteraction) error {
	query := `
		INSERT INTO interacao_conteudo
		(event_id, id_conteudo, id_usuario, tipo, dwell_seconds, posicao, algoritmo, experimento, nivel_friccao, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		ON DUPLICATE KEY UPDATE event_id = event_id
	`
	_, err := r.db.ExecContext(ctx, query, event.EventID, event.ContentID, event.UserID, event.Type,
		event.DwellSeconds, event.Position, event.Algorithm, event.Experiment, event.FrictionLevel, event.CreatedAt)
	return err
}
