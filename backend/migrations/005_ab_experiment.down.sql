DROP TABLE IF EXISTS experimento_exposicao;
ALTER TABLE usuario_configuracao
    DROP COLUMN consentimento_pesquisa_versao,
    DROP COLUMN consentimento_pesquisa;
