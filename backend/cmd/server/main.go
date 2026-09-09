package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/be-productive/backend/internal/adapter/http/router"
	"github.com/be-productive/backend/internal/adapter/repository/mysql"
	"github.com/be-productive/backend/internal/infrastructure/config"
	"github.com/be-productive/backend/internal/infrastructure/database"
	"github.com/be-productive/backend/internal/usecase/user"
	"github.com/joho/godotenv"
)

func main() {
	// Load .env file
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: No .env file found (using defaults/system env)")
	}

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Connect to database
	db, err := database.Connect(cfg.Database)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Start Privacy Anonimization Job (UC18)
	userRepo := mysql.NewUserRepository(db)
	anonJob := user.NewAnonimizeJob(userRepo)
	go anonJob.StartScheduler(context.Background(), 24*time.Hour)
	log.Println("Anonimization background job started (24h interval)")

	// Setup router
	r := router.New(db, cfg)

	// Start server
	addr := cfg.Server.Host + ":" + cfg.Server.Port
	log.Printf("Server starting on %s", addr)

	server := &http.Server{
		Addr: addr, Handler: r,
		ReadTimeout: cfg.Server.ReadTimeout, WriteTimeout: cfg.Server.WriteTimeout,
		IdleTimeout: cfg.Server.IdleTimeout, ReadHeaderTimeout: 5 * time.Second,
	}
	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server shutdown failed: %v", err)
	}
}
