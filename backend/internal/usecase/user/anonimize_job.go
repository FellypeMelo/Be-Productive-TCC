package user

import (
	"context"
	"log"
	"time"

	"github.com/be-productive/backend/internal/domain"
)

type AnonimizerRepository interface {
	GetInactiveUsers(ctx context.Context, threshold time.Time) ([]domain.User, error)
	AnonimizeUser(ctx context.Context, userID int64) error
}

type AnonimizeJob struct {
	repo AnonimizerRepository
}

func NewAnonimizeJob(repo AnonimizerRepository) *AnonimizeJob {
	return &AnonimizeJob{repo: repo}
}

// Run executes the anonimization process (UC18)
func (j *AnonimizeJob) Run(ctx context.Context) {
	// Threshold: 2 years (UC18/RF016)
	threshold := time.Now().AddDate(-2, 0, 0)

	log.Printf("[AnonimizeJob] Checking for users inactive since %v", threshold)

	users, err := j.repo.GetInactiveUsers(ctx, threshold)
	if err != nil {
		log.Printf("[AnonimizeJob] Error fetching inactive users: %v", err)
		return
	}

	log.Printf("[AnonimizeJob] Found %d users to anonimize", len(users))

	for _, user := range users {
		log.Printf("[AnonimizeJob] Anonimizing user ID: %d", user.ID)
		if err := j.repo.AnonimizeUser(ctx, user.ID); err != nil {
			log.Printf("[AnonimizeJob] Failed to anonimize user %d: %v", user.ID, err)
		}
	}
}

// StartScheduler starts the job periodically (KISS: Simple goroutine)
func (j *AnonimizeJob) StartScheduler(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			j.Run(ctx)
		}
	}
}
