-- Migration: Create core tables
-- Version: 001

-- Users table
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_criptografada VARCHAR(255) NOT NULL,
    estado_emocional_inferido ENUM('NEUTRO', 'POSITIVO', 'NEGATIVO', 'ESTRESSADO') DEFAULT 'NEUTRO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Topics table
CREATE TABLE IF NOT EXISTS topico (
    id_topico INT AUTO_INCREMENT PRIMARY KEY,
    nome_topico VARCHAR(100) NOT NULL,
    descricao TEXT
);

-- User-Topic relationship (RF002: 3-5 topics)
CREATE TABLE IF NOT EXISTS usuario_topico (
    id_usuario INT NOT NULL,
    id_topico INT NOT NULL,
    PRIMARY KEY (id_usuario, id_topico),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_topico) REFERENCES topico(id_topico) ON DELETE CASCADE
);

-- Communities table
CREATE TABLE IF NOT EXISTS comunidade (
    id_comunidade INT AUTO_INCREMENT PRIMARY KEY,
    nome_comunidade VARCHAR(255) NOT NULL,
    topico_principal_id INT NOT NULL,
    regras_de_moderacao TEXT,
    FOREIGN KEY (topico_principal_id) REFERENCES topico(id_topico)
);

-- Content table (RF005, RF006)
CREATE TABLE IF NOT EXISTS conteudo (
    id_conteudo INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    tipo_de_midia ENUM('TEXTO', 'VIDEO', 'AUDIO') NOT NULL,
    categoria ENUM('PRODUTIVIDADE', 'ENTRETENIMENTO') NOT NULL,
    autor_id INT NOT NULL,
    data_publicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags_relevantes VARCHAR(500),
    score_de_qualidade DECIMAL(5,4) DEFAULT 0.5000,
    FOREIGN KEY (autor_id) REFERENCES usuario(id_usuario)
);

-- Content-Topic relationship
CREATE TABLE IF NOT EXISTS conteudo_topico (
    id_conteudo INT NOT NULL,
    id_topico INT NOT NULL,
    PRIMARY KEY (id_conteudo, id_topico),
    FOREIGN KEY (id_conteudo) REFERENCES conteudo(id_conteudo) ON DELETE CASCADE,
    FOREIGN KEY (id_topico) REFERENCES topico(id_topico) ON DELETE CASCADE
);

-- Focus Goals table (RF009, RF010)
CREATE TABLE IF NOT EXISTS meta_de_foco (
    id_meta INT AUTO_INCREMENT PRIMARY KEY,
    usuario_associado_id INT NOT NULL,
    categoria ENUM('PRODUTIVIDADE', 'ENTRETENIMENTO') NOT NULL,
    duracao_definida INT NOT NULL, -- in minutes
    status ENUM('ATIVA', 'PAUSADA', 'CONCLUIDA') DEFAULT 'ATIVA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_associado_id) REFERENCES usuario(id_usuario)
);

-- Sessions table (RF011, RF013)
CREATE TABLE IF NOT EXISTS sessao_de_uso (
    id_sessao INT AUTO_INCREMENT PRIMARY KEY,
    usuario_associado_id INT NOT NULL,
    hora_inicio TIMESTAMP NOT NULL,
    hora_fim TIMESTAMP NULL,
    tempo_produtividade_realizado INT DEFAULT 0, -- in minutes
    tempo_entretenimento_realizado INT DEFAULT 0, -- in minutes
    feedback_da_sessao INT NULL CHECK (feedback_da_sessao BETWEEN 1 AND 5),
    FOREIGN KEY (usuario_associado_id) REFERENCES usuario(id_usuario)
);

-- Session-Goal relationship
CREATE TABLE IF NOT EXISTS sessao_meta (
    id_sessao INT NOT NULL,
    id_meta INT NOT NULL,
    PRIMARY KEY (id_sessao, id_meta),
    FOREIGN KEY (id_sessao) REFERENCES sessao_de_uso(id_sessao) ON DELETE CASCADE,
    FOREIGN KEY (id_meta) REFERENCES meta_de_foco(id_meta) ON DELETE CASCADE
);

-- Content Feedback table (RF015)
CREATE TABLE IF NOT EXISTS feedback_conteudo (
    id_feedback INT AUTO_INCREMENT PRIMARY KEY,
    id_conteudo INT NOT NULL,
    id_usuario INT NOT NULL,
    tipo ENUM('util', 'nao_relevante', 'relaxante') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_conteudo) REFERENCES conteudo(id_conteudo),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    UNIQUE KEY unique_feedback (id_conteudo, id_usuario)
);

-- Reports/Denunciations table (RF007)
CREATE TABLE IF NOT EXISTS denuncia (
    id_denuncia INT AUTO_INCREMENT PRIMARY KEY,
    id_conteudo INT NOT NULL,
    id_usuario INT NOT NULL,
    motivo ENUM('desinformacao', 'discurso_de_odio', 'assedio', 'violencia', 'fraude', 'outro') NOT NULL,
    detalhes TEXT,
    status ENUM('PENDENTE', 'EM_ANALISE', 'RESOLVIDA', 'REJEITADA') DEFAULT 'PENDENTE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_conteudo) REFERENCES conteudo(id_conteudo),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- Indexes for performance
CREATE INDEX idx_conteudo_categoria ON conteudo(categoria);
CREATE INDEX idx_conteudo_autor ON conteudo(autor_id);
CREATE INDEX idx_conteudo_score ON conteudo(score_de_qualidade DESC);
CREATE INDEX idx_sessao_usuario ON sessao_de_uso(usuario_associado_id);
CREATE INDEX idx_meta_usuario ON meta_de_foco(usuario_associado_id);
CREATE INDEX idx_denuncia_status ON denuncia(status);
