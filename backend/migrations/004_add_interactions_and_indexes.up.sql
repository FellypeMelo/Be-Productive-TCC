CREATE TABLE IF NOT EXISTS interacao_conteudo (
    id_interacao BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    id_conteudo INT NOT NULL,
    id_usuario INT NOT NULL,
    tipo ENUM('impression', 'open', 'complete', 'hide') NOT NULL,
    dwell_seconds INT NOT NULL DEFAULT 0,
    posicao INT NOT NULL DEFAULT 0,
    algoritmo VARCHAR(64) NOT NULL DEFAULT '',
    experimento VARCHAR(64) NOT NULL DEFAULT '',
    nivel_friccao ENUM('none', 'mild', 'high', 'block') NOT NULL DEFAULT 'none',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_conteudo) REFERENCES conteudo(id_conteudo) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_interacao_usuario_tempo (id_usuario, created_at),
    INDEX idx_interacao_conteudo_tipo (id_conteudo, tipo)
);

CREATE INDEX idx_conteudo_data ON conteudo(data_publicacao DESC);
