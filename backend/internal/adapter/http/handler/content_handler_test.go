package handler_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/be-productive/backend/internal/adapter/http/handler"
	"github.com/be-productive/backend/internal/domain"
	contentUsecase "github.com/be-productive/backend/internal/usecase/content"
	"github.com/stretchr/testify/assert"
)

// contextKey is used for injecting user_id into request context
type contextKey string

const userIDKey contextKey = "user_id"

// feedContentRepo returns feed data for GetFeed tests
type feedContentRepo struct{}

func (f *feedContentRepo) Create(ctx context.Context, c *domain.Content, topicIDs []int64) error {
	c.ID = 1
	return nil
}
func (f *feedContentRepo) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	return nil, nil
}
func (f *feedContentRepo) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	return []domain.Content{{ID: 1, Titulo: "Feed Item", DataPublicacao: time.Now()}}, nil
}
func (f *feedContentRepo) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	return []domain.Content{{ID: 1, Titulo: "Feed Item", DataPublicacao: time.Now()}}, nil
}
func (f *feedContentRepo) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	return nil
}
func (f *feedContentRepo) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	return nil
}
func (f *feedContentRepo) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	return nil
}

// createContentRepo for create tests
type createContentRepo struct{}

func (c *createContentRepo) Create(ctx context.Context, content *domain.Content, topicIDs []int64) error {
	content.ID = 1
	return nil
}
func (c *createContentRepo) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	return nil, nil
}
func (c *createContentRepo) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	return nil, nil
}
func (c *createContentRepo) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	return nil, nil
}
func (c *createContentRepo) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	return nil
}
func (c *createContentRepo) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	return nil
}
func (c *createContentRepo) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	return nil
}

// idContentRepo for GetByID tests
type idContentRepo struct{}

func (i *idContentRepo) Create(ctx context.Context, c *domain.Content, topicIDs []int64) error {
	return nil
}
func (i *idContentRepo) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	if id == 1 {
		return &domain.Content{ID: 1, Titulo: "Test Content", DataPublicacao: time.Now()}, nil
	}
	return nil, domain.ErrNotFound
}
func (i *idContentRepo) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	return nil, nil
}
func (i *idContentRepo) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	return nil, nil
}
func (i *idContentRepo) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	return nil
}
func (i *idContentRepo) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	return nil
}
func (i *idContentRepo) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	return nil
}

// feedbackContentRepo for SubmitFeedback tests
type feedbackContentRepo struct{}

func (f *feedbackContentRepo) Create(ctx context.Context, c *domain.Content, topicIDs []int64) error {
	return nil
}
func (f *feedbackContentRepo) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	return &domain.Content{ID: 1, ScoreDeQualidade: 0.5, DataPublicacao: time.Now()}, nil
}
func (f *feedbackContentRepo) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	return nil, nil
}
func (f *feedbackContentRepo) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	return nil, nil
}
func (f *feedbackContentRepo) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	return nil
}
func (f *feedbackContentRepo) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	return nil
}
func (f *feedbackContentRepo) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	return nil
}

// reportContentRepo for Report tests
type reportContentRepo struct{}

func (r *reportContentRepo) Create(ctx context.Context, c *domain.Content, topicIDs []int64) error {
	return nil
}
func (r *reportContentRepo) GetByID(ctx context.Context, id int64) (*domain.Content, error) {
	return nil, nil
}
func (r *reportContentRepo) GetByIDs(ctx context.Context, ids []int64) ([]domain.Content, error) {
	return nil, nil
}
func (r *reportContentRepo) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int) ([]domain.Content, error) {
	return nil, nil
}
func (r *reportContentRepo) UpdateQualityScore(ctx context.Context, id int64, score float64) error {
	return nil
}
func (r *reportContentRepo) AddFeedback(ctx context.Context, contentID, userID int64, feedbackType string) error {
	return nil
}
func (r *reportContentRepo) AddReport(ctx context.Context, contentID, userID int64, motivo, detalhes string) error {
	return nil
}

// contextWrapper injects user_id into context for authenticated endpoints
type contextWrapper struct {
	handler http.Handler
}

func (cw *contextWrapper) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := context.WithValue(r.Context(), "user_id", int64(1))
	cw.handler.ServeHTTP(w, r.WithContext(ctx))
}

// newTestMux creates a router that mimics the production mux patterns
func newTestMux(h *handler.ContentHandler) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /feed", h.GetFeed)
	mux.HandleFunc("POST /content", h.Create)
	mux.HandleFunc("GET /content/{id}", h.GetByID)
	mux.HandleFunc("POST /content/{id}/feedback", h.SubmitFeedback)
	mux.HandleFunc("POST /content/{id}/report", h.Report)
	return &contextWrapper{handler: mux}
}

func TestGetFeedReturns200(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&feedContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	req := httptest.NewRequest("GET", "/feed?limit=10", nil)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
	var resp map[string]any
	json.NewDecoder(rr.Body).Decode(&resp)
	assert.True(t, resp["success"].(bool))
	data := resp["data"].(map[string]any)
	assert.NotNil(t, data["content_ids"])
	assert.NotNil(t, data["items"])
	assert.NotNil(t, data["friction_level"])
}

func TestCreateValidContent(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&createContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	body := strings.NewReader(`{
		"titulo": "New Content",
		"corpo": "body text",
		"tipo_de_midia": "TEXTO",
		"categoria": "PRODUTIVIDADE",
		"autor_id": 1,
		"topic_ids": [1, 2],
		"tags": "test"
	}`)

	req := httptest.NewRequest("POST", "/content", body)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusCreated, rr.Code)
}

func TestCreateInvalidJSON(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&createContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	body := strings.NewReader(`not json`)
	req := httptest.NewRequest("POST", "/content", body)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusBadRequest, rr.Code)
}

func TestCreateMissingTopics(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&createContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	body := strings.NewReader(`{"titulo":"No Topics","corpo":"x","tipo_de_midia":"TEXTO","categoria":"PRODUTIVIDADE","autor_id":1,"topic_ids":[],"tags":""}`)
	req := httptest.NewRequest("POST", "/content", body)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusBadRequest, rr.Code)
	assert.Contains(t, rr.Body.String(), "at least one topic")
}

func TestCreateInvalidCategory(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&createContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	body := strings.NewReader(`{"titulo":"Bad Cat","corpo":"x","tipo_de_midia":"TEXTO","categoria":"INVALID","autor_id":1,"topic_ids":[1],"tags":""}`)
	req := httptest.NewRequest("POST", "/content", body)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusBadRequest, rr.Code)
}

func TestGetContentByID(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&idContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	req := httptest.NewRequest("GET", "/content/1", nil)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
	var resp map[string]any
	json.NewDecoder(rr.Body).Decode(&resp)
	// Response is wrapped in {success, data} envelope
	assert.True(t, resp["success"].(bool))
	data := resp["data"].(map[string]any)
	assert.Equal(t, "Test Content", data["titulo"])
}

func TestGetContentByIDNotFound(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&idContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	req := httptest.NewRequest("GET", "/content/999", nil)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusNotFound, rr.Code)
}

func TestSubmitFeedback(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&feedbackContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	body := strings.NewReader(`{"user_id": 1, "type": "util"}`)
	req := httptest.NewRequest("POST", "/content/1/feedback", body)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
}

func TestReportContent(t *testing.T) {
	h := handler.NewContentHandler(contentUsecase.NewService(
		&reportContentRepo{}, "http://localhost:8002"))
	app := newTestMux(h)

	body := strings.NewReader(`{"user_id": 1, "motivo": "desinformacao", "detalhes": "fake news"}`)
	req := httptest.NewRequest("POST", "/content/1/report", body)
	rr := httptest.NewRecorder()

	app.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)
}

