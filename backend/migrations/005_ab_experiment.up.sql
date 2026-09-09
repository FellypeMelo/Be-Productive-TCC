-- Migration: Consent and idempotent exposure contract for sustainable-attention-v1
-- Version: 005

ALTER TABLE usuario_configuracao
    ADD COLUMN consentimento_pesquisa BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN consentimento_pesquisa_versao VARCHAR(32) NOT NULL DEFAULT '';

CREATE TABLE IF NOT EXISTS experimento_exposicao (
    id_exposicao BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    experiment_id VARCHAR(64) NOT NULL,
    variant ENUM('control', 'treatment') NOT NULL,
    assignment_version VARCHAR(64) NOT NULL,
    algorithm_version VARCHAR(64) NOT NULL,
    request_id VARCHAR(128) NOT NULL,
    id_usuario INT NOT NULL,
    eligible BOOLEAN NOT NULL DEFAULT TRUE,
    served BOOLEAN NOT NULL DEFAULT FALSE,
    fallback BOOLEAN NOT NULL DEFAULT FALSE,
    position_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_exposicao_experimento_variante (experiment_id, variant, created_at),
    INDEX idx_exposicao_usuario_experimento (id_usuario, experiment_id, created_at)
);
