package user

import (
	"context"
	"testing"

	"github.com/be-productive/backend/internal/domain"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type mockUserRepo struct {
	users     map[int64]*domain.User
	ByEmail   map[string]*domain.User
	topics    map[int64][]domain.Topic
	settings  *domain.UserSettings
	idCounter int64
}

func newMockUserRepo() *mockUserRepo {
	return &mockUserRepo{
		users:   make(map[int64]*domain.User),
		ByEmail: make(map[string]*domain.User),
		topics:  make(map[int64][]domain.Topic),
	}
}

func (m *mockUserRepo) Create(ctx context.Context, user *domain.User) error {
	m.idCounter++
	user.ID = m.idCounter
	m.users[user.ID] = user
	m.ByEmail[user.Email] = user
	return nil
}
func (m *mockUserRepo) GetByID(ctx context.Context, id int64) (*domain.User, error) {
	if u, ok := m.users[id]; ok {
		return u, nil
	}
	return nil, domain.ErrNotFound
}
func (m *mockUserRepo) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
	if u, ok := m.ByEmail[email]; ok {
		return u, nil
	}
	return nil, domain.ErrNotFound
}
func (m *mockUserRepo) Update(ctx context.Context, user *domain.User) error {
	m.users[user.ID] = user
	return nil
}
func (m *mockUserRepo) AddTopics(ctx context.Context, userID int64, topicIDs []int64) error {
	for _, tid := range topicIDs {
		m.topics[userID] = append(m.topics[userID], domain.Topic{ID: tid, NomeTopico: "topic"})
	}
	return nil
}
func (m *mockUserRepo) GetTopics(ctx context.Context, userID int64) ([]domain.Topic, error) {
	return m.topics[userID], nil
}
func (m *mockUserRepo) GetSettings(ctx context.Context, userID int64) (*domain.UserSettings, error) {
	return &domain.UserSettings{
		UsuarioID:             userID,
		SugestaoSaudavelAtiva: true,
		PersonalizacaoAtiva:   true,
		NotificacaoFocoAtiva:  false,
	}, nil
}
func (m *mockUserRepo) UpdateSettings(ctx context.Context, settings *domain.UserSettings) error {
	m.settings = settings
	return nil
}

func TestCreateUser(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, err := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	require.NoError(t, err)
	assert.Equal(t, "Alice", user.Nome)
	assert.Equal(t, "NEUTRO", user.EstadoEmocionalInferido)
	assert.NotEmpty(t, user.SenhaCriptografada)
	assert.NotEqual(t, "password123", user.SenhaCriptografada) // password should be hashed
}

func TestCreateUserDuplicateEmail(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, err := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")
	require.NoError(t, err)

	_, err = svc.Create(context.Background(), "Alice2", "alice@test.com", "password456")
	assert.ErrorIs(t, err, domain.ErrAlreadyExists)
}

func TestCreateUserShortPassword(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, err := svc.Create(context.Background(), "Alice", "alice@test.com", "short")
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
}

func TestCreateUserExactly8CharPassword(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, err := svc.Create(context.Background(), "Alice", "alice@test.com", "12345678") // exactly 8
	assert.NoError(t, err)
}

func TestCreateUser7CharPassword(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, err := svc.Create(context.Background(), "Alice", "alice@test.com", "1234567") // 7 chars
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
}

func TestCreateUserEmptyName(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, err := svc.Create(context.Background(), "", "alice@test.com", "password123")
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
}

func TestLoginSuccess(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, _ = svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	token, user, err := svc.Login(context.Background(), "alice@test.com", "password123")

	require.NoError(t, err)
	assert.Equal(t, "Alice", user.Nome)
	assert.NotEmpty(t, token)
}

func TestLoginWrongPassword(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, _ = svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	_, _, err := svc.Login(context.Background(), "alice@test.com", "wrongpassword")
	assert.ErrorIs(t, err, domain.ErrInvalidCredentials)
}

func TestLoginNonExistentUser(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, _, err := svc.Login(context.Background(), "nobody@test.com", "password123")
	assert.ErrorIs(t, err, domain.ErrInvalidCredentials)
}

func TestUpdateUserName(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, _ := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	updated, err := svc.Update(context.Background(), user.ID, "Alice Updated")

	require.NoError(t, err)
	assert.Equal(t, "Alice Updated", updated.Nome)
}

func TestUpdateUserEmptyNameDoesNotClear(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, _ := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	updated, err := svc.Update(context.Background(), user.ID, "")

	require.NoError(t, err)
	assert.Equal(t, "Alice", updated.Nome) // not cleared
}

func TestUpdateNonExistentUser(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	_, err := svc.Update(context.Background(), 999, "Nobody")
	assert.ErrorIs(t, err, domain.ErrNotFound)
}

func TestSelectTopicsValidRange(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, _ := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	err := svc.SelectTopics(context.Background(), user.ID, []int64{1, 2, 3})
	assert.NoError(t, err)

	topics, _ := svc.GetTopics(context.Background(), user.ID)
	assert.Equal(t, 3, len(topics))
}

func TestSelectTopicsMaxValid(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, _ := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	err := svc.SelectTopics(context.Background(), user.ID, []int64{1, 2, 3, 4, 5})
	assert.NoError(t, err)
}

func TestSelectTopicsTooFew(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, _ := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	err := svc.SelectTopics(context.Background(), user.ID, []int64{1})
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "between 3 and 5")
}

func TestSelectTopicsTooMany(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	user, _ := svc.Create(context.Background(), "Alice", "alice@test.com", "password123")

	err := svc.SelectTopics(context.Background(), user.ID, []int64{1, 2, 3, 4, 5, 6})
	assert.Error(t, err)
}

func TestSelectTopicsNonExistentUser(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	err := svc.SelectTopics(context.Background(), 999, []int64{1, 2, 3})
	assert.ErrorIs(t, err, domain.ErrNotFound)
}

func TestSettingsCRUD(t *testing.T) {
	repo := newMockUserRepo()
	svc := NewService(repo, "test-secret")

	settings, err := svc.GetSettings(context.Background(), 1)
	require.NoError(t, err)
	assert.True(t, settings.SugestaoSaudavelAtiva)
	assert.True(t, settings.PersonalizacaoAtiva)
	assert.False(t, settings.NotificacaoFocoAtiva)

	err = svc.UpdateSettings(context.Background(), &domain.UserSettings{
		UsuarioID:             1,
		SugestaoSaudavelAtiva: false,
		PersonalizacaoAtiva:   false,
		NotificacaoFocoAtiva:  true,
	})
	assert.NoError(t, err)
}

func TestHashPasswordIsDeterministic(t *testing.T) {
	h1 := hashPassword("same-password")
	h2 := hashPassword("same-password")
	assert.Equal(t, h1, h2) // SHA256 always produces same output for same input
}

func TestHashPasswordDifferentInputs(t *testing.T) {
	h1 := hashPassword("password1")
	h2 := hashPassword("password2")
	assert.NotEqual(t, h1, h2)
}
