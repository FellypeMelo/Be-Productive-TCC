package community

import (
	"context"

	"github.com/be-productive/backend/internal/domain"
)

type Repository interface {
	List(ctx context.Context) ([]domain.Community, error)
	Join(ctx context.Context, userID, communityID int64) error
	Leave(ctx context.Context, userID, communityID int64) error
	GetUserCommunities(ctx context.Context, userID int64) ([]domain.Community, error)
}

type Service struct {
	repo Repository
}

func NewService(repo Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) List(ctx context.Context) ([]domain.Community, error) {
	return s.repo.List(ctx)
}

func (s *Service) Join(ctx context.Context, userID, communityID int64) error {
	return s.repo.Join(ctx, userID, communityID)
}

func (s *Service) Leave(ctx context.Context, userID, communityID int64) error {
	return s.repo.Leave(ctx, userID, communityID)
}

func (s *Service) GetUserCommunities(ctx context.Context, userID int64) ([]domain.Community, error) {
	return s.repo.GetUserCommunities(ctx, userID)
}
