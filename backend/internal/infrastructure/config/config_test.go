package config

import "testing"

func TestLoadRequiresStrongJWTSecret(t *testing.T) {
	t.Setenv("JWT_SECRET", "short")
	if _, err := Load(); err == nil {
		t.Fatal("expected weak JWT secret to be rejected")
	}
}

func TestLoadProductionRequiresInternalSecret(t *testing.T) {
	t.Setenv("APP_ENV", "production")
	t.Setenv("JWT_SECRET", "12345678901234567890123456789012")
	t.Setenv("RECOMMENDER_SHARED_SECRET", "")
	if _, err := Load(); err == nil {
		t.Fatal("expected missing production internal secret to be rejected")
	}
}

func TestLoadParsesAllowedOrigins(t *testing.T) {
	t.Setenv("JWT_SECRET", "12345678901234567890123456789012")
	t.Setenv("ALLOWED_ORIGINS", "https://app.example, https://admin.example")
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	if len(cfg.Server.AllowedOrigins) != 2 {
		t.Fatalf("expected 2 origins, got %d", len(cfg.Server.AllowedOrigins))
	}
}
