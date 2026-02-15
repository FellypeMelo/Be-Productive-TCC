package handler

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/be-productive/backend/internal/usecase/focus"
)

type FocusHandler struct {
	service *focus.Service
}

func NewFocusHandler(service *focus.Service) *FocusHandler {
	return &FocusHandler{service: service}
}

// CreateGoal creates a new focus goal (RF009)
func (h *FocusHandler) CreateGoal(w http.ResponseWriter, r *http.Request) {
	var req struct {
		UserID              int64 `json:"user_id"`
		TempoProdutividade  int   `json:"tempo_produtividade"`  // minutes
		TempoEntretenimento int   `json:"tempo_entretenimento"` // minutes
		ModoAbsoluto        bool  `json:"modo_absoluto"`        // RF010
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	// Validate at least one time > 0
	if req.TempoProdutividade <= 0 && req.TempoEntretenimento <= 0 {
		respondError(w, http.StatusBadRequest, "at least one category must have time > 0")
		return
	}

	goals, err := h.service.CreateGoal(r.Context(), focus.CreateGoalInput{
		UserID:              req.UserID,
		TempoProdutividade:  req.TempoProdutividade,
		TempoEntretenimento: req.TempoEntretenimento,
		ModoAbsoluto:        req.ModoAbsoluto,
	})
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusCreated, goals)
}

// ListGoals lists user's focus goals
func (h *FocusHandler) ListGoals(w http.ResponseWriter, r *http.Request) {
	userIDStr := r.URL.Query().Get("user_id")
	userID, err := strconv.ParseInt(userIDStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid user_id")
		return
	}

	goals, err := h.service.ListGoals(r.Context(), userID)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, goals)
}

// ListSessions lists focus sessions
func (h *FocusHandler) ListSessions(w http.ResponseWriter, r *http.Request) {
	userIDStr := r.URL.Query().Get("user_id")
	userID, err := strconv.ParseInt(userIDStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid user_id")
		return
	}

	activeOnly := r.URL.Query().Get("active") == "true"

	sessions, err := h.service.ListSessions(r.Context(), userID, activeOnly)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, sessions)
}

// GetSessionGoals lists goals for a session
func (h *FocusHandler) GetSessionGoals(w http.ResponseWriter, r *http.Request) {
	idStr := r.PathValue("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid session ID")
		return
	}

	goals, err := h.service.GetSessionGoals(r.Context(), id)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, goals)
}

// StartSession starts a focus session (RF011)
func (h *FocusHandler) StartSession(w http.ResponseWriter, r *http.Request) {
	var req struct {
		UserID       int64   `json:"user_id"`
		GoalIDs      []int64 `json:"goal_ids"`
		ModoAbsoluto bool    `json:"modo_absoluto"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	session, err := h.service.StartSession(r.Context(), req.UserID, req.GoalIDs, req.ModoAbsoluto)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusCreated, session)
}

// EndSession ends a focus session (RF013)
func (h *FocusHandler) EndSession(w http.ResponseWriter, r *http.Request) {
	idStr := r.PathValue("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid session ID")
		return
	}

	var req struct {
		TempoProdutividadeRealizado  int  `json:"tempo_produtividade_realizado"`
		TempoEntretenimentoRealizado int  `json:"tempo_entretenimento_realizado"`
		Feedback                     *int `json:"feedback"` // 1-5
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	session, err := h.service.EndSession(r.Context(), id, focus.EndSessionInput{
		TempoProdutividadeRealizado:  req.TempoProdutividadeRealizado,
		TempoEntretenimentoRealizado: req.TempoEntretenimentoRealizado,
		Feedback:                     req.Feedback,
	})
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, session)
}

// GetReport generates session report (RF013)
func (h *FocusHandler) GetReport(w http.ResponseWriter, r *http.Request) {
	idStr := r.PathValue("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		respondError(w, http.StatusBadRequest, "invalid session ID")
		return
	}

	report, err := h.service.GetReport(r.Context(), id)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, report)
}
