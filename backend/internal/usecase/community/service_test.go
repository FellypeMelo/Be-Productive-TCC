package community_test

import (
	"context"
	"testing"

	"github.com/be-productive/backend/internal/domain"
	"github.com/be-productive/backend/internal/usecase/community"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type mockCommunityRepo struct {
	communities []domain.Community
	userJoined  map[int64][]int64 // userID → communityIDs
}

func newMockRepo() *mockCommunityRepo {
	return &mockCommunityRepo{
		communities: []domain.Community{
			{ID: 1, NomeComunidade: "Focus Group", TopicoPrincipalID: 1},
			{ID: 2, NomeComunidade: "Chill Zone", TopicoPrincipalID: 2},
		},
		userJoined: make(map[int64][]int64),
	}
}

func (m *mockCommunityRepo) List(ctx context.Context) ([]domain.Community, error) {
	return m.communities, nil
}
func (m *mockCommunityRepo) Join(ctx context.Context, userID, communityID int64) error {
	m.userJoined[userID] = append(m.userJoined[userID], communityID)
	return nil
}
func (m *mockCommunityRepo) Leave(ctx context.Context, userID, communityID int64) error {
	joined := m.userJoined[userID]
	for i, cid := range joined {
		if cid == communityID {
			m.userJoined[userID] = append(joined[:i], joined[i+1:]...)
			break
		}
	}
	return nil
}
func (m *mockCommunityRepo) GetUserCommunities(ctx context.Context, userID int64) ([]domain.Community, error) {
	joinedIDs := m.userJoined[userID]
	var results []domain.Community
	for _, cid := range joinedIDs {
		for _, c := range m.communities {
			if c.ID == cid {
				results = append(results, c)
				break
			}
		}
	}
	return results, nil
}

func TestListCommunities(t *testing.T) {
	repo := newMockRepo()
	svc := community.NewService(repo)

	communities, err := svc.List(context.Background())
	require.NoError(t, err)
	assert.Equal(t, 2, len(communities))
	assert.Equal(t, "Focus Group", communities[0].NomeComunidade)
	assert.Equal(t, "Chill Zone", communities[1].NomeComunidade)
}

func TestJoinCommunity(t *testing.T) {
	repo := newMockRepo()
	svc := community.NewService(repo)

	err := svc.Join(context.Background(), 1, 1)
	require.NoError(t, err)

	userComms, _ := svc.GetUserCommunities(context.Background(), 1)
	assert.Equal(t, 1, len(userComms))
	assert.Equal(t, "Focus Group", userComms[0].NomeComunidade)
}

func TestJoinCommunityMultiple(t *testing.T) {
	repo := newMockRepo()
	svc := community.NewService(repo)

	svc.Join(context.Background(), 1, 1)
	svc.Join(context.Background(), 1, 2)

	userComms, _ := svc.GetUserCommunities(context.Background(), 1)
	assert.Equal(t, 2, len(userComms))
}

func TestLeaveCommunity(t *testing.T) {
	repo := newMockRepo()
	svc := community.NewService(repo)

	svc.Join(context.Background(), 1, 1)
	err := svc.Leave(context.Background(), 1, 1)
	require.NoError(t, err)

	userComms, _ := svc.GetUserCommunities(context.Background(), 1)
	assert.Equal(t, 0, len(userComms))
}

func TestLeaveCommunityNotJoined(t *testing.T) {
	repo := newMockRepo()
	svc := community.NewService(repo)

	// Leaving a community you never joined should not error
	err := svc.Leave(context.Background(), 1, 99)
	assert.NoError(t, err)
}

func TestUserHasNoCommunities(t *testing.T) {
	repo := newMockRepo()
	svc := community.NewService(repo)

	userComms, _ := svc.GetUserCommunities(context.Background(), 99)
	assert.Equal(t, 0, len(userComms))
}
