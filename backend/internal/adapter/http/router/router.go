package router

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"time"

	"github.com/be-productive/backend/internal/adapter/http/handler"
	"github.com/be-productive/backend/internal/adapter/http/middleware"
	"github.com/be-productive/backend/internal/adapter/repository/mysql"
	"github.com/be-productive/backend/internal/infrastructure/config"
	"github.com/be-productive/backend/internal/usecase/community"
	"github.com/be-productive/backend/internal/usecase/content"
	"github.com/be-productive/backend/internal/usecase/focus"
	"github.com/be-productive/backend/internal/usecase/user"
)

func New(db *sql.DB, cfg *config.Config) http.Handler {
	mux := http.NewServeMux()
	metrics := middleware.NewMetrics()
	globalLimiter := middleware.NewRateLimiter(cfg.Server.RateLimit, time.Minute)
	authLimiter := middleware.NewRateLimiter(10, time.Minute)

	// Repositories
	userRepo := mysql.NewUserRepository(db)
	contentRepo := mysql.NewContentRepository(db)
	focusRepo := mysql.NewFocusRepository(db)
	communityRepo := mysql.NewCommunityRepository(db)

	// Services
	userService := user.NewService(userRepo, cfg.JWTSecret)
	contentService := content.NewService(
		contentRepo,
		cfg.Recommender.URL,
		content.WithSharedSecret(cfg.Recommender.SharedSecret),
		content.WithFocusGateway(focusRepo),
	)
	focusService := focus.NewService(focusRepo)
	communityService := community.NewService(communityRepo)

	// Handlers
	userHandler := handler.NewUserHandler(userService)
	contentHandler := handler.NewContentHandler(contentService)
	focusHandler := handler.NewFocusHandler(focusService)
	communityHandler := handler.NewCommunityHandler(communityService)

	// Health check
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok"}`))
	})
	mux.HandleFunc("GET /health/ready", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		ctx, cancel := context.WithTimeout(r.Context(), time.Second)
		defer cancel()
		if err := db.PingContext(ctx); err != nil {
			w.WriteHeader(http.StatusServiceUnavailable)
			_ = json.NewEncoder(w).Encode(map[string]string{"status": "not_ready", "database": "unavailable"})
			return
		}
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ready", "database": "connected"})
	})
	mux.Handle("GET /metrics", metrics)

	// Auth routes (Public)
	mux.Handle("POST /api/v1/auth/login", authLimiter.Middleware(http.HandlerFunc(userHandler.Login)))
	mux.Handle("POST /api/v1/auth/register", authLimiter.Middleware(http.HandlerFunc(userHandler.Create)))

	// Auth Middleware
	auth := middleware.AuthMiddleware([]byte(cfg.JWTSecret))

	// User routes (Protected)
	mux.Handle("GET /api/v1/users/{id}", auth(http.HandlerFunc(userHandler.GetByID)))
	mux.Handle("PUT /api/v1/users/{id}", auth(http.HandlerFunc(userHandler.Update)))
	mux.Handle("POST /api/v1/users/{id}/topics", auth(http.HandlerFunc(userHandler.SelectTopics)))
	mux.Handle("GET /api/v1/users/{id}/topics", auth(http.HandlerFunc(userHandler.GetTopics)))
	mux.Handle("GET /api/v1/users/{id}/settings", auth(http.HandlerFunc(userHandler.GetSettings)))
	mux.Handle("PUT /api/v1/users/{id}/settings", auth(http.HandlerFunc(userHandler.UpdateSettings)))

	// Content routes (Protected)
	mux.Handle("POST /api/v1/content", auth(http.HandlerFunc(contentHandler.Create)))
	mux.Handle("GET /api/v1/content/{id}", auth(http.HandlerFunc(contentHandler.GetByID)))
	mux.Handle("POST /api/v1/content/{id}/feedback", auth(http.HandlerFunc(contentHandler.SubmitFeedback)))
	mux.Handle("POST /api/v1/content/{id}/report", auth(http.HandlerFunc(contentHandler.Report)))
	mux.Handle("POST /api/v1/content/{id}/events", auth(http.HandlerFunc(contentHandler.RecordInteraction)))

	// Community routes (Protected) (UC04)
	mux.Handle("GET /api/v1/communities", auth(http.HandlerFunc(communityHandler.List)))
	mux.Handle("POST /api/v1/communities/{id}/join", auth(http.HandlerFunc(communityHandler.Join)))
	mux.Handle("POST /api/v1/communities/{id}/leave", auth(http.HandlerFunc(communityHandler.Leave)))
	mux.Handle("GET /api/v1/communities/me", auth(http.HandlerFunc(communityHandler.GetUserCommunities)))

	// Feed routes (Protected)
	mux.Handle("GET /api/v1/feed", auth(http.HandlerFunc(contentHandler.GetFeed)))

	// Focus routes (Protected)
	mux.Handle("POST /api/v1/focus/goals", auth(http.HandlerFunc(focusHandler.CreateGoal)))
	mux.Handle("GET /api/v1/focus/goals", auth(http.HandlerFunc(focusHandler.ListGoals)))
	mux.Handle("GET /api/v1/focus/sessions", auth(http.HandlerFunc(focusHandler.ListSessions)))
	mux.Handle("GET /api/v1/focus/sessions/{id}/goals", auth(http.HandlerFunc(focusHandler.GetSessionGoals)))
	mux.Handle("POST /api/v1/focus/sessions", auth(http.HandlerFunc(focusHandler.StartSession)))
	mux.Handle("PUT /api/v1/focus/sessions/{id}", auth(http.HandlerFunc(focusHandler.EndSession)))
	mux.Handle("GET /api/v1/focus/sessions/{id}/report", auth(http.HandlerFunc(focusHandler.GetReport)))

	// Apply middleware
	handler := middleware.BodyLimit(1<<20, mux)
	handler = globalLimiter.Middleware(handler)
	handler = metrics.Middleware(handler)
	handler = middleware.Logger(handler)
	handler = middleware.CORS(cfg.Server.AllowedOrigins, handler)
	handler = middleware.SecurityHeaders(handler)
	handler = middleware.RequestID(handler)
	handler = middleware.Recover(handler)

	return handler
}
