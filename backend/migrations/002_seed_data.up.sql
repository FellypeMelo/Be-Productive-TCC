-- Seed data for development

-- Insert sample topics
INSERT INTO topico (nome_topico, descricao) VALUES
    ('Tecnologia', 'Novidades e tendências em tecnologia'),
    ('Produtividade', 'Dicas e ferramentas para ser mais produtivo'),
    ('Saúde Mental', 'Bem-estar e cuidados com a mente'),
    ('Música', 'Descobertas musicais e playlists'),
    ('Filmes', 'Recomendações e reviews de filmes'),
    ('Jogos', 'Novidades do mundo gamer'),
    ('Leitura', 'Livros e artigos interessantes'),
    ('Exercícios', 'Fitness e atividades físicas'),
    ('Meditação', 'Práticas de mindfulness'),
    ('Culinária', 'Receitas e dicas culinárias');

-- Insert test user
INSERT INTO usuario (nome, email, senha_criptografada, estado_emocional_inferido) VALUES
    ('Usuário Teste', 'teste@beproductive.com', '5e884898da28047d9165141404e42d4c3bce4c1e816c1f0e3ee0e8ae2f39d0c5', 'NEUTRO');

-- Link test user to topics
INSERT INTO usuario_topico (id_usuario, id_topico) VALUES
    (1, 1), (1, 2), (1, 3);
