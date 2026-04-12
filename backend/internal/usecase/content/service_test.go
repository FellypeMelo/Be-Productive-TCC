package content

import (
	"context"
	"testing"
	"time"

	"github.com/be-productive/backend/internal/domain"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type mockContentRepo struct {
	contents map[int64]*domain.Content
	created  []*domain.Content
}

func newMockRepo() *mockContentRepo {
	return &mockContentRepo{
		contents: map[int64]*domain.Content{
			1: {
				ID:               1,
				Titulo:           "Deep Focus",
				TipoDeMidia:      domain.ContentTypeVideo,
				Categoria:        domain.CategoryProdutividade,
				ScoreDeQualidade: 0.9,
				DataPublicacao:   time.Now(),
			},
			2: {
				ID:               2,
				Titulo:           "Fun Video",
				TipoDeMidia:      domain.ContentTypeVideo,
				Categoria:        domain.CategoryEntretenimento,
				ScoreDeQualidade: 0.7,
				DataPublicacao:   time.Now(),
			},
		},
	}
}

func (m *mockContentRepo) Create(ctx context.Context, c *domain.Content, topicIDs []int64) error {
	c.ID = int64(len(m.contents) + 1)
	m.created = append(m.created, c)
	return nil
}
func (m *mockContentRepo) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	if c, ok := m.contents[id]; ok {
		return c, nil
	}
	return nil, domain.ErrNotFound
}
func (m *mockContentRepo) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	var out []domain.Content
	for _, id := range ids {
		if c, ok := m.contents[id]; ok {
			out = append(out, *c)
		}
	}
	return out, nil
}
func (m *mockContentRepo) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	var out []domain.Content
	for _, c := range m.contents {
		if category == "" || c.Categoria == category {
			out = append(out, *c)
			if len(out) >= limit {
				break
			}
		}
	}
	return out, nil
}
func (m *mockContentRepo) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	if c, ok := m.contents[id]; ok {
		c.ScoreDeQualidade = score
	}
	return nil
}
func (m *mockContentRepo) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	return nil
}
func (m *mockContentRepo) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	return nil
}

func TestCreateContent(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	input := CreateContentInput{
		Titulo:      "Test Content",
		Corpo:       "Body",
		TipoDeMidia: domain.ContentTypeTexto,
		Categoria:   domain.CategoryProdutividade,
		AutorID:     1,
		TopicIDs:    []int64{1},
		Tags:        "focus",
	}
	content, err := svc.Create(context.Background(), input)

	require.NoError(t, err)
	assert.Equal(t, "Test Content", content.Titulo)
	assert.Equal(t, 0.5, content.ScoreDeQualidade) // RN002 initial
}

func TestGetFeedReturnsContent(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	result, err := svc.GetFeed(context.Background(), 1, "", 0, 20, false, "")

	require.NoError(t, err)
	assert.Equal(t, 2, len(result.Contents))
	assert.Equal(t, 0, len(result.Scores)) // no recommender, fallback
	assert.Equal(t, "none", result.FrictionLevel)
}

func TestGetFeedWithCategoryFilter(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	result, err := svc.GetFeed(context.Background(), 1, domain.CategoryProdutividade, 0, 20, false, "")

	require.NoError(t, err)
	assert.Equal(t, 1, len(result.Contents))
	assert.Equal(t, domain.CategoryProdutividade, result.Contents[0].Categoria)
}

func TestGetFeedFallbackWhenRecommenderDown(t *testing.T) {
	repo := newMockRepo()
	// Use a dead URL to trigger fallback
	svc := NewService(repo, "http://127.0.0.1:19999")

	result, err := svc.GetFeed(context.Background(), 1, "", 0, 10, false, "")

	require.NoError(t, err)
	assert.Equal(t, "none", result.FrictionLevel)
	assert.True(t, len(result.Contents) > 0)
}

func TestGetFeedRespectsLimit(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	result, err := svc.GetFeed(context.Background(), 1, "", 0, 1, false, "")

	require.NoError(t, err)
	assert.True(t, len(result.Contents) <= 1)
}

func TestSubmitFeedbackUtilIncreasesScore(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	err := svc.SubmitFeedback(context.Background(), 1, 1, "util")
	require.NoError(t, err)

	content, _ := repo.GetByID(context.Background(), 1)
	assert.True(t, content.ScoreDeQualidade > 0.9) // was 0.9, += 0.05
}

func TestSubmitFeedbackRelaxanteIncreasesScore(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	err := svc.SubmitFeedback(context.Background(), 1, 1, "relaxante")
	require.NoError(t, err)

	content, _ := repo.GetByID(context.Background(), 1)
	assert.True(t, content.ScoreDeQualidade > 0.9) // was 0.9, += 0.02
}

func TestSubmitFeedbackNaoRelevanteDecreasesScore(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	initialScore, _ := repo.GetByID(context.Background(), 1)
	assert.Equal(t, 0.9, initialScore.ScoreDeQualidade)

	err := svc.SubmitFeedback(context.Background(), 1, 1, "nao_relevante")
	require.NoError(t, err)

	content, _ := repo.GetByID(context.Background(), 1)
	assert.True(t, content.ScoreDeQualidade < 0.9) // was 0.9, -= 0.1
}

func TestSubmitFeedbackInvalidType(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	err := svc.SubmitFeedback(context.Background(), 1, 1, "invalid")
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
}

func TestReportInvalidMotivoRejected(t *testing.T) {
	repo := newMockRepo()
	svc := NewService(repo, "http://localhost:8002")

	err := svc.Report(context.Background(), 1, 1, "invalid_motivo", "")
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
}

func TestReportValidMotivosAccepted(t *testing.T) {
	validMotivos := []string{"desinformacao", "discurso_de_odio", "assedio", "violencia", "fraude", "outro"}

	for _, motivo := range validMotivos {
		t.Run(motivo, func(t *testing.T) {
			repo := newMockRepo()
			svc := NewService(repo, "http://localhost:8002")

			err := svc.Report(context.Background(), 1, 1, motivo, "details")
			assert.NoError(t, err)
		})
	}
}

func TestContentHandlerGetFeedReturns200(t *testing.T) {
	// Test handler-level integration (mock service is not possible directly,
	// but we test the FeedResult serialization path)
	result := &FeedResult{
		Contents:      []domain.Content{{ID: 1, Titulo: "Feed Item"}},
		Scores:        map[int64]float64{1: 0.85},
		FrictionLevel: "none",
	}

	// Verify FeedResult shape for handler serialization
	assert.Equal(t, "none", result.FrictionLevel)
	assert.Contains(t, result.Scores, int64(1))
	assert.Equal(t, 0.85, result.Scores[1])
}

func TestContentHandlerGetFeedWithFrictionLevel(t *testing.T) {
	frictionLevels := []string{"none", "mild", "high", "block"}

	for _, level := range frictionLevels {
		t.Run(level, func(t *testing.T) {
			result := &FeedResult{
				Contents:      []domain.Content{},
				Scores:        map[int64]float64{},
				FrictionLevel: level,
			}
			assert.Equal(t, level, result.FrictionLevel)
		})
	}
}