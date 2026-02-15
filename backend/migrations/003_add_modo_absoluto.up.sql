-- Migration: Add modo_absoluto to sessao_de_uso
-- Version: 003

ALTER TABLE sessao_de_uso ADD COLUMN modo_absoluto BOOLEAN DEFAULT FALSE;
