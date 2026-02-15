-- Migration: Add midia_url to conteudo
-- Version: 002

ALTER TABLE conteudo ADD COLUMN midia_url VARCHAR(500) AFTER corpo;
