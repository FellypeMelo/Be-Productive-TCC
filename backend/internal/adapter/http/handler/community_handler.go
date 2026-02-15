package handler

import (
	"net/http"
	"strconv"

	"github.com/be-productive/backend/internal/usecase/community"
)

type CommunityHandler struct {
	service *community.Service
}

func NewCommunityHandler(service *community.Service) *CommunityHandler {
	return &CommunityHandler{service: service}
}

func (h *CommunityHandler) List(w http.ResponseWriter, r *http.Request) {
	comms, err := h.service.List(r.Context())
	if err != nil {
		handleError(w, err)
		return
	}
	respondJSON(w, http.StatusOK, comms)
}

func (h *CommunityHandler) Join(w http.ResponseWriter, r *http.Request) {
	communityID, _ := strconv.ParseInt(r.PathValue("id"), 10, 64)
	userID, ok := r.Context().Value("user_id").(int64)
	if !ok {
		respondError(w, http.StatusUnauthorized, "user_id not found in token")
		return
	}

	if err := h.service.Join(r.Context(), userID, communityID); err != nil {
		handleError(w, err)
		return
	}
	respondJSON(w, http.StatusOK, map[string]bool{"success": true})
}

func (h *CommunityHandler) Leave(w http.ResponseWriter, r *http.Request) {
	communityID, _ := strconv.ParseInt(r.PathValue("id"), 10, 64)
	userID, ok := r.Context().Value("user_id").(int64)
	if !ok {
		respondError(w, http.StatusUnauthorized, "user_id not found in token")
		return
	}

	if err := h.service.Leave(r.Context(), userID, communityID); err != nil {
		handleError(w, err)
		return
	}
	respondJSON(w, http.StatusOK, map[string]bool{"success": true})
}

func (h *CommunityHandler) GetUserCommunities(w http.ResponseWriter, r *http.Request) {
	userID, ok := r.Context().Value("user_id").(int64)
	if !ok {
		respondError(w, http.StatusUnauthorized, "user_id not found in token")
		return
	}
	comms, err := h.service.GetUserCommunities(r.Context(), userID)
	if err != nil {
		handleError(w, err)
		return
	}
	respondJSON(w, http.StatusOK, comms)
}
