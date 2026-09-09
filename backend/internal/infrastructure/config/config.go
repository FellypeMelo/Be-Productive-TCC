package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

type Config struct {
	Server      ServerConfig
	Database    DatabaseConfig
	Recommender RecommenderConfig
	JWTSecret   string
	Environment string
}

type ServerConfig struct {
	Host           string
	Port           string
	AllowedOrigins []string
	ReadTimeout    time.Duration
	WriteTimeout   time.Duration
	IdleTimeout    time.Duration
	RateLimit      int
}

type DatabaseConfig struct {
	Host     string
	Port     string
	User     string
	Password string
	Name     string
}

type RecommenderConfig struct {
	URL          string
	SharedSecret string
}

func Load() (*Config, error) {
	environment := strings.ToLower(getEnv("APP_ENV", "development"))
	jwtSecret := strings.TrimSpace(os.Getenv("JWT_SECRET"))
	if len(jwtSecret) < 32 {
		return nil, fmt.Errorf("JWT_SECRET must contain at least 32 characters")
	}
	sharedSecret := strings.TrimSpace(os.Getenv("RECOMMENDER_SHARED_SECRET"))
	if environment == "production" && len(sharedSecret) < 32 {
		return nil, fmt.Errorf("RECOMMENDER_SHARED_SECRET must contain at least 32 characters in production")
	}
	rateLimit, err := strconv.Atoi(getEnv("RATE_LIMIT_PER_MINUTE", "240"))
	if err != nil || rateLimit < 1 {
		return nil, fmt.Errorf("RATE_LIMIT_PER_MINUTE must be a positive integer")
	}

	cfg := &Config{
		Server: ServerConfig{
			Host:           getEnv("SERVER_HOST", "localhost"),
			Port:           getEnv("SERVER_PORT", "8080"),
			AllowedOrigins: splitCSV(getEnv("ALLOWED_ORIGINS", "http://localhost:5173")),
			ReadTimeout:    10 * time.Second,
			WriteTimeout:   15 * time.Second,
			IdleTimeout:    60 * time.Second,
			RateLimit:      rateLimit,
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnv("DB_PORT", "3306"),
			User:     getEnv("DB_USER", "root"),
			Password: getEnv("DB_PASSWORD", ""),
			Name:     getEnv("DB_NAME", "be_productive"),
		},
		Recommender: RecommenderConfig{
			URL:          getEnv("RECOMMENDER_URL", "http://localhost:8002"),
			SharedSecret: sharedSecret,
		},
		JWTSecret:   jwtSecret,
		Environment: environment,
	}
	return cfg, nil
}

func splitCSV(value string) []string {
	parts := strings.Split(value, ",")
	result := make([]string, 0, len(parts))
	for _, part := range parts {
		if origin := strings.TrimSpace(part); origin != "" {
			result = append(result, origin)
		}
	}
	return result
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
