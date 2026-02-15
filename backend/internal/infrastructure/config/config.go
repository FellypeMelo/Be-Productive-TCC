package config

import (
	"os"
)

type Config struct {
	Server      ServerConfig
	Database    DatabaseConfig
	Recommender RecommenderConfig
	JWTSecret   string
}

type ServerConfig struct {
	Host string
	Port string
}

type DatabaseConfig struct {
	Host     string
	Port     string
	User     string
	Password string
	Name     string
}

type RecommenderConfig struct {
	URL string
}

func Load() (*Config, error) {
	return &Config{
		Server: ServerConfig{
			Host: getEnv("SERVER_HOST", "localhost"),
			Port: getEnv("SERVER_PORT", "8080"),
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnv("DB_PORT", "3306"),
			User:     getEnv("DB_USER", "root"),
			Password: getEnv("DB_PASSWORD", ""),
			Name:     getEnv("DB_NAME", "be_productive"),
		},
		Recommender: RecommenderConfig{
			URL: getEnv("RECOMMENDER_URL", "http://localhost:8002"),
		},
		JWTSecret: getEnv("JWT_SECRET", "be_productive_secret_key_123"),
	}, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
