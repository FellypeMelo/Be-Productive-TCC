package user

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"time"

	"github.com/be-productive/backend/internal/domain"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

// Repository defines the user storage interface
type Repository interface {
	Create(ctx context.Context, user *domain.User) error
	GetByID(ctx context.Context, id int64) (*domain.User, error)
	GetByEmail(ctx context.Context, email string) (*domain.User, error)
	Update(ctx context.Context, user *domain.User) error
	AddTopics(ctx context.Context, userID int64, topicIDs []int64) error
	GetTopics(ctx context.Context, userID int64) ([]domain.Topic, error)
	GetSettings(ctx context.Context, userID int64) (*domain.UserSettings, error)
	UpdateSettings(ctx context.Context, settings *domain.UserSettings) error
}

// Service handles user business logic
type Service struct {
	repo   Repository
	jwtKey []byte
}

// NewService creates a new user service
func NewService(repo Repository, jwtKey string) *Service {
	return &Service{
		repo:   repo,
		jwtKey: []byte(jwtKey),
	}
}

// Create registers a new user (RF001)
func (s *Service) Create(ctx context.Context, nome, email, senha string) (*domain.User, error) {
	// Check if email exists
	existing, _ := s.repo.GetByEmail(ctx, email)
	if existing != nil {
		return nil, domain.ErrAlreadyExists
	}

	// Validate input
	if nome == "" || email == "" || len(senha) < 8 {
		return nil, domain.ErrInvalidInput
	}

	// Hash password with bcrypt (salted, slow — replaces legacy SHA-256)
	hashedBytes, err := bcrypt.GenerateFromPassword([]byte(senha), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}
	hashedPassword := string(hashedBytes)

	user := &domain.User{
		Nome:                    nome,
		Email:                   email,
		SenhaCriptografada:      hashedPassword,
		EstadoEmocionalInferido: "NEUTRO",
		CreatedAt:               time.Now(),
		UpdatedAt:               time.Now(),
	}

	if err := s.repo.Create(ctx, user); err != nil {
		return nil, err
	}

	return user, nil
}

// GetByID retrieves a user by ID
func (s *Service) GetByID(ctx context.Context, id int64) (*domain.User, error) {
	return s.repo.GetByID(ctx, id)
}

// Update modifies user information (RF003)
func (s *Service) Update(ctx context.Context, id int64, nome string) (*domain.User, error) {
	user, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if nome != "" {
		user.Nome = nome
	}
	user.UpdatedAt = time.Now()

	if err := s.repo.Update(ctx, user); err != nil {
		return nil, err
	}

	return user, nil
}

// SelectTopics associates topics with user during onboarding (RF002)
func (s *Service) SelectTopics(ctx context.Context, userID int64, topicIDs []int64) error {
	// Verify user exists
	_, err := s.repo.GetByID(ctx, userID)
	if err != nil {
		return err
	}

	// Validate 3-5 topics
	if len(topicIDs) < 3 || len(topicIDs) > 5 {
		return errors.New("must select between 3 and 5 topics")
	}

	return s.repo.AddTopics(ctx, userID, topicIDs)
}

// GetTopics retrieves user's topics
func (s *Service) GetTopics(ctx context.Context, userID int64) ([]domain.Topic, error) {
	return s.repo.GetTopics(ctx, userID)
}

// Login authenticates a user and returns the token + user data
func (s *Service) Login(ctx context.Context, email, senha string) (string, *domain.User, error) {
	user, err := s.repo.GetByEmail(ctx, email)
	if err != nil {
		return "", nil, domain.ErrInvalidCredentials
	}

	if isLegacyHash(user.SenhaCriptografada) {
		// Legacy SHA-256 hash: verify with the old method, then transparently
		// upgrade the stored hash to bcrypt on successful login.
		if user.SenhaCriptografada != hashPassword(senha) {
			return "", nil, domain.ErrInvalidCredentials
		}
		if newHash, hashErr := bcrypt.GenerateFromPassword([]byte(senha), bcrypt.DefaultCost); hashErr == nil {
			user.SenhaCriptografada = string(newHash)
			user.UpdatedAt = time.Now()
			_ = s.repo.Update(ctx, user)
		}
	} else if err := bcrypt.CompareHashAndPassword([]byte(user.SenhaCriptografada), []byte(senha)); err != nil {
		// Constant-time bcrypt comparison
		return "", nil, domain.ErrInvalidCredentials
	}

	// Generate JWT token
	token, err := s.generateToken(user.ID, user.Email)
	if err != nil {
		return "", nil, err
	}
	return token, user, nil
}

// Helper functions

// hashPassword computes the legacy SHA-256 hash. Retained only to verify (and then
// upgrade) pre-existing accounts created before the bcrypt migration.
func hashPassword(password string) string {
	hash := sha256.Sum256([]byte(password))
	return hex.EncodeToString(hash[:])
}

// isLegacyHash reports whether a stored hash is a 64-char hex SHA-256 digest
// (bcrypt hashes start with "$2" and are 60 chars, so they never match).
func isLegacyHash(hash string) bool {
	if len(hash) != 64 {
		return false
	}
	for _, c := range hash {
		isHex := (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')
		if !isHex {
			return false
		}
	}
	return true
}

type Claims struct {
	UserID int64  `json:"user_id"`
	Email  string `json:"email"`
	jwt.RegisteredClaims
}

func (s *Service) generateToken(userID int64, email string) (string, error) {
	expirationTime := time.Now().Add(24 * time.Hour)
	claims := &Claims{
		UserID: userID,
		Email:  email,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expirationTime),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(s.jwtKey)
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

// GetSettings retrieves user preferences (UC17)
func (s *Service) GetSettings(ctx context.Context, userID int64) (*domain.UserSettings, error) {
	return s.repo.GetSettings(ctx, userID)
}

// UpdateSettings modifies user preferences (UC17)
func (s *Service) UpdateSettings(ctx context.Context, settings *domain.UserSettings) error {
	return s.repo.UpdateSettings(ctx, settings)
}
