package handler

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/be-productive/backend/internal/domain"
	"github.com/be-productive/backend/internal/usecase/user"
)

type UserHandler struct {
	service *user.Service
}

func NewUserHandler(service *user.Service) *UserHandler {
	return &UserHandler{service: service}
}

// Create handles user registration
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Nome  string `json:"nome"`
		Email string `json:"email"`
		Senha string `json:"senha"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	user, err := h.service.Create(r.Context(), req.Nome, req.Email, req.Senha)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusCreated, user)
}

// GetByID retrieves the authenticated user (identity derived from the JWT, not the path)
func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	id, ok := currentUserID(w, r)
	if !ok {
		return
	}

	user, err := h.service.GetByID(r.Context(), id)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, user)
}

// Update modifies user information (identity derived from the JWT, not the path)
func (h *UserHandler) Update(w http.ResponseWriter, r *http.Request) {
	id, ok := currentUserID(w, r)
	if !ok {
		return
	}

	var req struct {
		Nome string `json:"nome"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	user, err := h.service.Update(r.Context(), id, req.Nome)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, user)
}

// SelectTopics handles topic selection during onboarding (identity from the JWT)
func (h *UserHandler) SelectTopics(w http.ResponseWriter, r *http.Request) {
	id, ok := currentUserID(w, r)
	if !ok {
		return
	}

	var req struct {
		TopicIDs []int64 `json:"topic_ids"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	// Validate 3-5 topics (RF002)
	if len(req.TopicIDs) < 3 || len(req.TopicIDs) > 5 {
		respondError(w, http.StatusBadRequest, "must select between 3 and 5 topics")
		return
	}

	err := h.service.SelectTopics(r.Context(), id, req.TopicIDs)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, map[string]bool{"success": true})
}

// GetTopics retrieves the authenticated user's topics (identity from the JWT)
func (h *UserHandler) GetTopics(w http.ResponseWriter, r *http.Request) {
	id, ok := currentUserID(w, r)
	if !ok {
		return
	}

	topics, err := h.service.GetTopics(r.Context(), id)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, topics)
}

// Login authenticates a user
func (h *UserHandler) Login(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Email string `json:"email"`
		Senha string `json:"senha"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	token, user, err := h.service.Login(r.Context(), req.Email, req.Senha)
	if err != nil {
		handleError(w, err)
		return
	}

	respondJSON(w, http.StatusOK, map[string]interface{}{
		"token": token,
		"user": map[string]interface{}{
			"id_usuario":                user.ID,
			"nome":                      user.Nome,
			"email":                     user.Email,
			"estado_emocional_inferido": user.EstadoEmocionalInferido,
		},
	})
}

// GetSettings retrieves user configuration (UC17)
func (h *UserHandler) GetSettings(w http.ResponseWriter, r *http.Request) {
	userID, ok := currentUserID(w, r)
	if !ok {
		return
	}
	settings, err := h.service.GetSettings(r.Context(), userID)
	if err != nil {
		handleError(w, err)
		return
	}
	respondJSON(w, http.StatusOK, settings)
}

// UpdateSettings updates user configuration (UC17)
func (h *UserHandler) UpdateSettings(w http.ResponseWriter, r *http.Request) {
	userID, ok := currentUserID(w, r)
	if !ok {
		return
	}
	var settings domain.UserSettings
	if err := json.NewDecoder(r.Body).Decode(&settings); err != nil {
		respondError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	settings.UsuarioID = userID

	if err := h.service.UpdateSettings(r.Context(), &settings); err != nil {
		handleError(w, err)
		return
	}
	respondJSON(w, http.StatusOK, settings)
}

// Helper functions

// userIDFromContext reads the authenticated user id injected by AuthMiddleware.
func userIDFromContext(r *http.Request) (int64, bool) {
	uid, ok := r.Context().Value("user_id").(int64)
	return uid, ok
}

// authUserID returns the authenticated user id, writing a 401 response if absent.
func authUserID(w http.ResponseWriter, r *http.Request) (int64, bool) {
	uid, ok := userIDFromContext(r)
	if !ok {
		respondError(w, http.StatusUnauthorized, "user_id not found in token")
		return 0, false
	}
	return uid, true
}

// currentUserID returns the authenticated user id for "current user" routes. If the
// request carries an {id} path value that differs from the token, it responds 403 and
// returns ok=false, preventing horizontal privilege escalation (IDOR).
func currentUserID(w http.ResponseWriter, r *http.Request) (int64, bool) {
	authID, ok := authUserID(w, r)
	if !ok {
		return 0, false
	}
	if idStr := r.PathValue("id"); idStr != "" {
		id, err := strconv.ParseInt(idStr, 10, 64)
		if err != nil {
			respondError(w, http.StatusBadRequest, "invalid user ID")
			return 0, false
		}
		if id != authID {
			respondError(w, http.StatusForbidden, "cannot access another user's resource")
			return 0, false
		}
	}
	return authID, true
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"data":    data,
	})
}

func respondError(w http.ResponseWriter, status int, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error": map[string]string{
			"message": message,
		},
	})
}

func handleError(w http.ResponseWriter, err error) {
	switch err {
	case domain.ErrNotFound:
		respondError(w, http.StatusNotFound, err.Error())
	case domain.ErrUnauthorized, domain.ErrInvalidCredentials:
		respondError(w, http.StatusUnauthorized, err.Error())
	case domain.ErrForbidden:
		respondError(w, http.StatusForbidden, err.Error())
	case domain.ErrInvalidInput:
		respondError(w, http.StatusBadRequest, err.Error())
	case domain.ErrAlreadyExists:
		respondError(w, http.StatusConflict, err.Error())
	default:
		respondError(w, http.StatusInternalServerError, "internal server error")
	}
}
