package handler

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/be-productive/backend/internal/domain"
	"github.com/be-productive/backend/internal/usecase/content"
)

type ContentHandler struct {
	service *content.Service
}

func NewContentHandler(service *content.Service) *ContentHandler {
	return &ContentHandler{service: service}
}

// Create handles content publication
func (h *ContentHandler) Create(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Titulo      string  `json:"titulo"`
		Corpo       string  `json:"corpo"`
		TipoDeMidia string  `json:"tipo_de_midia"`
		Categoria   string  `json:"categoria"`
		AutorID     int64   `json:"autor_id"`
		TopicIDs    []int64 `json:"topic_ids"`
		Tags        string  `json:"tags"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	// Validate category (RF006)
	if req.Categoria != string(domain.CategoryProdutividade) &&
		req.Categoria != string(domain.CategoryEntretenimento) {
		respondError(w, http.StatusBadRequest, "category must be PRODUTIVIDADE or ENTRETENIMENTO")
		return
	}

	// Validate at least one topic
	if len(req.TopicIDs) == 0 {
		respondError(w, http.StatusBadRequest, "must associate with at least one topic")
		return
	}

	content, err := h.service.Create(r.Context(), content.CreateContentInput{
		Titulo:      req.Titulo,
		Corpo:       req.Corpo,
		TipoDeMidia: domain.ContentType(req.TipoDeMidia),
		Categoria:   domain.ContentCategory(req.Categoria),
		AutorID:     req.AutorID,
		TopicIDs:    req.TopicIDs,
		Tags:        req.Tags,
	})
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusCreated, content)
}

// GetByID retrieves content by ID
func (h *ContentHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	idStr := r.PathValue("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid content ID")
		return
	}

	content, err := h.service.GetByID(r.Context(), id)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, content)
}

// GetFeed returns personalized feed
func (h *ContentHandler) GetFeed(w http.ResponseWriter, r *http.Request) {
	// 1. Get user_id from context (injected by AuthMiddleware)
	userID, ok := r.Context().Value("user_id").(int64)
	if !ok {
		// Fallback to query param if needed, but for security, token is better
		userIDStr := r.URL.Query().Get("user_id")
		uid, err := strconv.ParseInt(userIDStr, 10, 64)
		if err != nil {
			respondError(w, http.StatusUnauthorized, "user_id not found in context or query")
			return
		}
		userID = uid
	}

	category := r.URL.Query().Get("category")
	topicIDStr := r.URL.Query().Get("topic_id")
	limitStr := r.URL.Query().Get("limit")
	absoluteModeStr := r.URL.Query().Get("absolute_mode_active")
	declaredGoal := r.URL.Query().Get("declared_goal")

	topicID, _ := strconv.ParseInt(topicIDStr, 10, 64)

	limit := 20
	if limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 && l <= 50 {
			limit = l
		}
	}

	absoluteModeActive := absoluteModeStr == "true" || absoluteModeStr == "1"

	result, err := h.service.GetFeed(r.Context(), userID, domain.ContentCategory(category), topicID, limit, absoluteModeActive, declaredGoal)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, map[string]any{
		"content_ids":    extractContentIDs(result.Contents),
		"scores":         result.Scores,
		"items":          result.Contents,
		"friction_level": result.FrictionLevel,
	})
}

func extractContentIDs(contents []domain.Content) []int64 {
	ids := make([]int64, len(contents))
	for i, c := range contents {
		ids[i] = c.ID
	}
	return ids
}

// SubmitFeedback handles user feedback on content (RF015)
func (h *ContentHandler) SubmitFeedback(w http.ResponseWriter, r *http.Request) {
	idStr := r.PathValue("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid content ID")
		return
	}

	var req struct {
		UserID int64  `json:"user_id"`
		Type   string `json:"type"` // "util", "nao_relevante", "relaxante"
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	err = h.service.SubmitFeedback(r.Context(), id, req.UserID, req.Type)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, map[string]bool{"success": true})
}

// Report handles content reports (RF007)
func (h *ContentHandler) Report(w http.ResponseWriter, r *http.Request) {
	idStr := r.PathValue("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid content ID")
		return
	}

	var req struct {
		UserID   int64  `json:"user_id"`
		Motivo   string `json:"motivo"`
		Detalhes string `json:"detalhes"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	err = h.service.Report(r.Context(), id, req.UserID, req.Motivo, req.Detalhes)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, map[string]bool{"success": true})
}
