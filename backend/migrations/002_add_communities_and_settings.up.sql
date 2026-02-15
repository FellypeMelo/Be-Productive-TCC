-- Migration: Add communities and settings tables
-- Version: 002

-- User Settings table (UC17)
CREATE TABLE IF NOT EXISTS usuario_configuracao (
    id_usuario INT PRIMARY KEY,
    sugestao_saudavel_ativa BOOLEAN DEFAULT TRUE,
    personalizacao_ativa BOOLEAN DEFAULT TRUE,
    notificacao_foco_ativa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- User-Community relationship (UC04)
CREATE TABLE IF NOT EXISTS usuario_comunidade (
    id_usuario INT NOT NULL,
    id_comunidade INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_comunidade),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_comunidade) REFERENCES comunidade(id_comunidade) ON DELETE CASCADE
);
