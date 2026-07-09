-- ============================================================================
--  Be-Productive - Seed de dados realista (pt-BR)
-- ----------------------------------------------------------------------------
--  Objetivo: deixar a aplicacao "viva" para demonstracao/desenvolvimento.
--  Executar com:  mysql -u root -p be_productive < backend/scripts/mock_data.sql
--
--  SENHA DE ACESSO (todos os usuarios):  senha123
--  Hash gravado em senha_criptografada  :  SHA-256 hex de "senha123"
--      55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251
--
--  NOTA DE SEGURANCA: estes hashes sao SHA-256 (formato legado). O backend Go
--  reconhece o digest hex de 64 caracteres, valida o login pelo metodo antigo
--  e, no primeiro login bem-sucedido, RE-HASHEIA a senha para bcrypt de forma
--  transparente (ver backend/internal/usecase/user/service.go). Ou seja: apos
--  o primeiro login de cada conta o hash deixa de ser SHA-256 automaticamente.
-- ============================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- Limpeza (idempotente). FKs desligadas para permitir TRUNCATE em qualquer
-- ordem; religadas logo em seguida. Filhos antes dos pais por clareza.
-- ---------------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE denuncia;
TRUNCATE TABLE feedback_conteudo;
TRUNCATE TABLE sessao_meta;
TRUNCATE TABLE sessao_de_uso;
TRUNCATE TABLE meta_de_foco;
TRUNCATE TABLE usuario_configuracao;
TRUNCATE TABLE usuario_comunidade;
TRUNCATE TABLE usuario_topico;
TRUNCATE TABLE conteudo_topico;
TRUNCATE TABLE conteudo;
TRUNCATE TABLE comunidade;
TRUNCATE TABLE topico;
TRUNCATE TABLE usuario;
SET FOREIGN_KEY_CHECKS = 1;

-- ===========================================================================
-- 1) USUARIOS  (senha de todos = senha123)
-- ===========================================================================
INSERT INTO usuario (id_usuario, nome, email, senha_criptografada, estado_emocional_inferido) VALUES
(1,  'Ana Beatriz Ferreira',   'ana.ferreira@beprodutivo.com.br',   '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'POSITIVO'),
(2,  'Lucas Andrade Souza',    'lucas.souza@beprodutivo.com.br',    '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'NEUTRO'),
(3,  'Mariana Oliveira Costa', 'mariana.costa@beprodutivo.com.br',  '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'ESTRESSADO'),
(4,  'Pedro Henrique Lima',    'pedro.lima@beprodutivo.com.br',     '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'NEUTRO'),
(5,  'Juliana Rodrigues Alves','juliana.alves@beprodutivo.com.br',  '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'NEGATIVO'),
(6,  'Rafael Santos Pereira',  'rafael.pereira@beprodutivo.com.br', '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'POSITIVO'),
(7,  'Camila Nogueira Dias',   'camila.dias@beprodutivo.com.br',    '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'NEUTRO'),
(8,  'Gustavo Almeida Ribeiro','gustavo.ribeiro@beprodutivo.com.br','55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'ESTRESSADO'),
(9,  'Beatriz Carvalho Melo',  'beatriz.melo@beprodutivo.com.br',   '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'POSITIVO'),
(10, 'Thiago Martins Rocha',   'thiago.rocha@beprodutivo.com.br',   '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'NEUTRO'),
(11, 'Larissa Gomes Barbosa',  'larissa.barbosa@beprodutivo.com.br','55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'NEGATIVO'),
(12, 'Bruno Fernandes Cardoso','bruno.cardoso@beprodutivo.com.br',  '55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251', 'POSITIVO');

-- ===========================================================================
-- 2) TOPICOS  (dois mundos: produtividade e entretenimento)
-- ===========================================================================
INSERT INTO topico (id_topico, nome_topico, descricao) VALUES
(1,  'Produtividade',  'Metodos, rotinas e ferramentas para trabalhar com foco e menos ansiedade.'),
(2,  'Estudos',        'Tecnicas de aprendizagem, memoria e organizacao para estudantes.'),
(3,  'Programacao',    'Desenvolvimento de software, boas praticas e carreira em tecnologia.'),
(4,  'Saude Mental',   'Bem-estar emocional, mindfulness e equilibrio na vida digital.'),
(5,  'Filosofia',      'Ideias que ajudam a pensar melhor sobre a vida e as escolhas do dia a dia.'),
(6,  'Design',         'Design visual, UX e principios de comunicacao pela imagem.'),
(7,  'Ciencia',        'Descobertas, curiosidades e o que a ciencia diz sobre habitos e cognicao.'),
(8,  'Musica',         'Playlists, generos e o poder da musica no humor e na concentracao.'),
(9,  'Games',          'Jogos, cultura gamer e diversao consciente.'),
(10, 'Humor',          'Memes, comedia e o lado leve da internet para relaxar.');

-- ===========================================================================
-- 3) COMUNIDADES  (topico_principal_id referencia topico.id_topico)
-- ===========================================================================
INSERT INTO comunidade (id_comunidade, nome_comunidade, topico_principal_id, regras_de_moderacao) VALUES
(1, 'Foco Total',                  1, '1. Compartilhe metodos e rotinas reais. 2. Nada de spam ou autopromocao. 3. Respeite o tempo de foco alheio.'),
(2, 'Dev BR',                      3, '1. Duvidas tecnicas sao bem-vindas. 2. Poste codigo formatado. 3. Sem flame war entre linguagens.'),
(3, 'Mente Sa',                    4, '1. Acolhimento sempre. 2. Nao substituimos acompanhamento profissional. 3. Sinalize gatilhos antes de postar.'),
(4, 'Clube do Livro e Filosofia',  5, '1. Debata ideias, nao pessoas. 2. Cite as fontes. 3. Mantenha o respeito na divergencia.'),
(5, 'Gamers Conscientes',          9, '1. Diversao com equilibrio. 2. Sem toxidez no chat. 3. Divulgue jogos, nao pirataria.');

-- ===========================================================================
-- 4) CONTEUDOS  (autor_id referencia usuario.id_usuario)
--    categoria: PRODUTIVIDADE | ENTRETENIMENTO
--    tipo_de_midia: TEXTO | VIDEO | AUDIO
--    score_de_qualidade: DECIMAL(5,4) 0.0000 - 1.0000
-- ===========================================================================
INSERT INTO conteudo (id_conteudo, titulo, corpo, midia_url, tipo_de_midia, categoria, autor_id, data_publicacao, tags_relevantes, score_de_qualidade) VALUES
-- ---- Mundo PRODUTIVIDADE ----
(1,  'Tecnica Pomodoro: divida seu dia em blocos de foco', 'A tecnica Pomodoro alterna 25 minutos de foco total com 5 de pausa. Neste guia explico como adaptar os ciclos a sua energia e evitar a fadiga mental ao longo do dia.', 'https://picsum.photos/seed/pomodoro/800/450', 'TEXTO', 'PRODUTIVIDADE', 1,  '2026-06-02 09:15:00', 'foco,pomodoro,rotina,gestao de tempo', 0.9200),
(2,  'Deep Work: o guia do trabalho profundo', 'Trabalho profundo e a capacidade de se concentrar sem distracoes em tarefas cognitivamente exigentes. Reuni aqui as praticas de Cal Newport que mais funcionaram para mim.', 'https://picsum.photos/seed/deepwork/800/450', 'TEXTO', 'PRODUTIVIDADE', 6,  '2026-06-05 08:40:00', 'foco,deep work,concentracao', 0.8800),
(3,  '5 apps de produtividade que realmente funcionam em 2026', 'Testei dezenas de aplicativos por tres meses. Neste video mostro os cinco que sobreviveram a rotina e por que os outros viraram apenas mais uma distracao.', 'https://www.youtube.com/embed/pRpeEdMmmQ0', 'VIDEO', 'PRODUTIVIDADE', 10, '2026-06-08 19:10:00', 'apps,produtividade,ferramentas', 0.7900),
(4,  'Como criar o habito de estudar 1 hora por dia', 'Nao e sobre forca de vontade, e sobre design de ambiente. Explico o gatilho, a rotina e a recompensa que transformaram meus estudos em piloto automatico.', NULL, 'TEXTO', 'PRODUTIVIDADE', 2,  '2026-06-10 21:05:00', 'estudos,habitos,disciplina', 0.8500),
(5,  'Mapas mentais: aprenda qualquer assunto mais rapido', 'Mapas mentais conectam ideias do jeito que o cerebro gosta. Neste video desenho um mapa do zero e mostro como revisar em minutos o que levaria horas.', 'https://www.youtube.com/embed/5MgBikgcWnY', 'VIDEO', 'PRODUTIVIDADE', 7,  '2026-06-12 14:25:00', 'estudos,mapa mental,memoria', 0.8100),
(6,  'Revisao espacada: a ciencia da memoria de longo prazo', 'Esquecer faz parte do aprendizado. A revisao espacada usa o esquecimento a seu favor, revisando cada conteudo no momento exato antes de ele sumir da memoria.', 'https://picsum.photos/seed/revisao/800/450', 'TEXTO', 'PRODUTIVIDADE', 9,  '2026-06-14 10:50:00', 'estudos,ciencia,memoria,anki', 0.9000),
(7,  'Introducao ao Go: sua primeira API REST', 'Go e simples, rapido e otimo para APIs. Neste tutorial construimos um endpoint do zero com net/http, sem frameworks pesados, para voce entender o que acontece por baixo.', 'https://picsum.photos/seed/golang/800/450', 'TEXTO', 'PRODUTIVIDADE', 6,  '2026-06-16 11:30:00', 'programacao,go,backend,api', 0.9400),
(8,  'Svelte vs React: qual escolher em 2026', 'Compilador contra biblioteca em tempo de execucao. Comparo bundle size, curva de aprendizado e produtividade para ajudar voce a decidir sem hype.', 'https://www.youtube.com/embed/MnpuK0MK4vo', 'VIDEO', 'PRODUTIVIDADE', 12, '2026-06-18 20:00:00', 'programacao,svelte,react,frontend', 0.8300),
(9,  'Clean Architecture na pratica', 'Camadas que apontam para dentro, dominio que nao conhece o banco. Mostro com exemplos reais como isso reduz o acoplamento e facilita os testes.', NULL, 'TEXTO', 'PRODUTIVIDADE', 12, '2026-06-20 09:45:00', 'programacao,arquitetura,clean architecture', 0.9100),
(10, 'Debugging sem estresse: como investigar bugs', 'Bug nao e inimigo, e pista. Compartilho o metodo que uso para isolar o problema, ler a stack trace com calma e evitar o desespero das duas da manha.', 'https://picsum.photos/seed/debug/800/450', 'TEXTO', 'PRODUTIVIDADE', 4,  '2026-06-22 16:20:00', 'programacao,debug,boas praticas', 0.8600),
(11, 'Meditacao guiada de 10 minutos para comecar o dia', 'Uma meditacao curta para ancorar a atencao antes do trabalho. Respire junto e observe como a mente desacelera sem exigir nada de voce.', 'https://open.spotify.com/embed/track/5ChkMS8OtdzJeqyybCc9R5', 'AUDIO', 'PRODUTIVIDADE', 3,  '2026-06-24 07:05:00', 'saude mental,meditacao,mindfulness', 0.8900),
(12, 'Ansiedade no trabalho: sinais e como lidar', 'Coracao acelerado antes de abrir o e-mail? Listo os sinais mais comuns da ansiedade no trabalho e estrategias praticas para os momentos de pico.', 'https://picsum.photos/seed/ansiedade/800/450', 'TEXTO', 'PRODUTIVIDADE', 1,  '2026-06-25 13:15:00', 'saude mental,ansiedade,trabalho', 0.8700),
(13, 'Respiracao 4-7-8: acalme a mente em minutos', 'Inspire por 4, segure por 7, expire por 8. Este audio conduz o exercicio que ativa o sistema nervoso parassimpatico e reduz a tensao quase na hora.', 'https://open.spotify.com/embed/track/2takcwOaAZWiXggoSeN53i', 'AUDIO', 'PRODUTIVIDADE', 8,  '2026-06-26 22:40:00', 'saude mental,respiracao,relaxamento', 0.8400),
(14, 'Estoicismo para a vida moderna: licoes de Marco Aurelio', 'Concentre-se no que depende de voce e aceite o resto. As Meditacoes de Marco Aurelio continuam surpreendentemente uteis para a ansiedade do seculo XXI.', 'https://picsum.photos/seed/estoico/800/450', 'TEXTO', 'PRODUTIVIDADE', 5,  '2026-06-27 18:30:00', 'filosofia,estoicismo,autoconhecimento', 0.8800),
(15, 'O mito de Sisifo e por que ele importa hoje', 'Camus imaginava Sisifo feliz empurrando a pedra. Discuto como encontrar sentido na repeticao e no trabalho que parece nunca terminar.', NULL, 'TEXTO', 'PRODUTIVIDADE', 11, '2026-06-28 15:00:00', 'filosofia,camus,sentido', 0.8000),
(16, 'Principios de design: hierarquia visual explicada', 'Por que seu olho vai direto ao botao certo? Neste video mostro como tamanho, contraste e espaco guiam a atencao em qualquer interface.', 'https://www.youtube.com/embed/a5KYlHNKQB8', 'VIDEO', 'PRODUTIVIDADE', 7,  '2026-06-29 10:10:00', 'design,ux,hierarquia visual', 0.8200),
(17, 'Teoria das cores para quem nao e designer', 'Cores comunicam antes das palavras. Explico complementares, analogas e como montar uma paleta agradavel sem depender de sorte.', 'https://picsum.photos/seed/cores/800/450', 'TEXTO', 'PRODUTIVIDADE', 7,  '2026-06-30 12:35:00', 'design,cores,paleta', 0.7800),
(18, 'Por que dormimos? A ciencia do sono explicada', 'Dormir nao e tempo perdido, e manutencao do cerebro. Este video resume o que a neurociencia descobriu sobre memoria, humor e o preco de dormir mal.', 'https://www.youtube.com/embed/nm1TxQj9IsQ', 'VIDEO', 'PRODUTIVIDADE', 9,  '2026-07-01 21:20:00', 'ciencia,sono,cerebro,saude', 0.9000),
(19, 'Como funciona a dopamina e o vicio em telas', 'A dopamina nao e prazer, e antecipacao. Entender esse mecanismo ajuda a explicar o scroll infinito e a recuperar o controle da sua atencao.', 'https://picsum.photos/seed/dopamina/800/450', 'TEXTO', 'PRODUTIVIDADE', 1,  '2026-07-03 09:00:00', 'ciencia,dopamina,foco,saude mental', 0.9300),
(20, 'Planejamento semanal: o metodo que organizou minha vida', 'Toda sexta reservo 20 minutos para revisar a semana e planejar a proxima. Mostro o template simples que uso e por que ele reduz a sobrecarga de segunda.', NULL, 'TEXTO', 'PRODUTIVIDADE', 2,  '2026-07-05 17:45:00', 'produtividade,planejamento,rotina', 0.7600),
-- ---- Mundo ENTRETENIMENTO ----
(21, 'Playlist lo-fi para focar e relaxar', 'Batidas suaves e sem letra para preencher o silencio sem roubar sua atencao. Ideal para trabalhar, estudar ou apenas desacelerar no fim do dia.', 'https://open.spotify.com/embed/playlist/0vvXsWCC9xrXsKd4FyS8kM', 'AUDIO', 'ENTRETENIMENTO', 5,  '2026-06-03 20:30:00', 'musica,lofi,foco,relaxar', 0.7200),
(22, 'A evolucao do rock brasileiro em 10 musicas', 'Dos Mutantes ao rock dos anos 2000, tracei uma linha do tempo com dez faixas que contam como o Brasil fez o rock soar brasileiro.', 'https://picsum.photos/seed/rockbr/800/450', 'TEXTO', 'ENTRETENIMENTO', 11, '2026-06-07 19:50:00', 'musica,rock,brasil,cultura', 0.7000),
(23, 'Como a trilha sonora muda sua percepcao de um filme', 'A mesma cena vira comedia ou terror dependendo da musica. Neste video comparo trechos e mostro como o som manipula a sua emocao sem voce perceber.', 'https://www.youtube.com/embed/YQHsXMglC9A', 'VIDEO', 'ENTRETENIMENTO', 7,  '2026-06-11 22:15:00', 'musica,cinema,trilha sonora', 0.6800),
(24, 'Os melhores jogos indie de 2025 para relaxar', 'Nem todo jogo precisa ser competitivo. Selecionei indies calmos e bonitos, perfeitos para desestressar depois de um dia pesado.', 'https://picsum.photos/seed/indie/800/450', 'TEXTO', 'ENTRETENIMENTO', 10, '2026-06-13 23:00:00', 'games,indie,relaxar', 0.7400),
(25, 'Speedrun: a arte de zerar jogos em tempo recorde', 'Por tras de um recorde de speedrun ha centenas de horas de treino e uma comunidade apaixonada. Mostro os truques e a cultura por tras dessa modalidade.', 'https://www.youtube.com/embed/9bZkp7q19f0', 'VIDEO', 'ENTRETENIMENTO', 4,  '2026-06-17 21:40:00', 'games,speedrun,comunidade', 0.7100),
(26, 'Por que jogos cooperativos fazem bem para a mente', 'Jogar em equipe fortalece vinculos e reduz o estresse. Comento estudos e minha propria experiencia sobre o lado saudavel dos games cooperativos.', NULL, 'TEXTO', 'ENTRETENIMENTO', 9,  '2026-06-19 20:25:00', 'games,cooperativo,saude mental', 0.7700),
(27, 'Memes que definiram a internet brasileira', 'Do Nazare confusa ao cachorro caramelo, os memes contam a nossa historia recente. Reuni os classicos que todo brasileiro reconhece na hora.', 'https://picsum.photos/seed/memes/800/450', 'TEXTO', 'ENTRETENIMENTO', 5,  '2026-06-21 18:05:00', 'humor,memes,internet,brasil', 0.6000),
(28, 'Stand-up nacional: 5 comediantes para conhecer', 'A comedia stand-up brasileira esta em alta. Indico cinco nomes com estilos diferentes para voce rir e talvez pensar um pouco tambem.', 'https://www.youtube.com/embed/kJQP7kiw5Fk', 'VIDEO', 'ENTRETENIMENTO', 11, '2026-06-23 22:55:00', 'humor,stand-up,comedia', 0.6500),
(29, 'Podcast de humor para ouvir no transito', 'Transformar o transito em risada e possivel. Este episodio piloto tem papo leve e historias absurdas do cotidiano para encurtar o caminho.', 'https://open.spotify.com/embed/track/1mea3bSkSGXuIRvnydlB5b', 'AUDIO', 'ENTRETENIMENTO', 5,  '2026-06-24 08:20:00', 'humor,podcast,transito', 0.6300),
(30, 'Trilha sonora instrumental para leitura', 'Musica instrumental que acompanha sem competir com o livro. Um fundo tranquilo para mergulhar na leitura sem dispersar.', 'https://open.spotify.com/embed/playlist/37i9dQZF1DWWQRwui0ExPn', 'AUDIO', 'ENTRETENIMENTO', 7,  '2026-06-25 21:10:00', 'musica,instrumental,leitura', 0.7500),
(31, 'Retrospectiva: os games que marcaram os anos 2010', 'Uma decada de jogos inesqueciveis. Relembro os titulos que definiram tendencias e que ainda hoje aparecem em qualquer conversa entre gamers.', 'https://picsum.photos/seed/games2010/800/450', 'TEXTO', 'ENTRETENIMENTO', 10, '2026-06-27 20:40:00', 'games,retrospectiva,cultura gamer', 0.6900),
(32, 'Piadas de programador que so quem e dev entende', 'Por que os programadores confundem Halloween com Natal? Uma colecao leve de piadas de codigo para descontrair no fim do expediente.', NULL, 'TEXTO', 'ENTRETENIMENTO', 12, '2026-06-29 19:30:00', 'humor,programacao,dev', 0.5800),
(33, 'MPB relaxante para o fim de tarde', 'Uma selecao de MPB para desacelerar quando o sol comeca a baixar. Vozes calmas e violao para respirar fundo depois do trabalho.', 'https://open.spotify.com/embed/playlist/37i9dQZF1DX8Sz1gsYZdwj', 'AUDIO', 'ENTRETENIMENTO', 11, '2026-07-02 18:15:00', 'musica,mpb,relaxar', 0.7300),
(34, 'As melhores trilhas de videogames de todos os tempos', 'A musica de um jogo fica na memoria por decadas. Neste video reuno as trilhas mais marcantes e explico por que elas funcionam tao bem.', 'https://www.youtube.com/embed/OPf0YbXqDm0', 'VIDEO', 'ENTRETENIMENTO', 4,  '2026-07-04 21:00:00', 'games,musica,trilha sonora', 0.7200),
(35, 'Humor e saude: por que rir reduz o estresse', 'Rir libera endorfina e relaxa o corpo. Comento o que a ciencia diz sobre o riso e por que uma dose de humor faz parte de uma rotina saudavel.', 'https://picsum.photos/seed/riso/800/450', 'TEXTO', 'ENTRETENIMENTO', 9,  '2026-07-06 16:50:00', 'humor,saude mental,bem-estar', 0.7900);

-- ===========================================================================
-- 5) CONTEUDO_TOPICO  (liga conteudo aos topicos)
-- ===========================================================================
INSERT INTO conteudo_topico (id_conteudo, id_topico) VALUES
(1,1),(2,1),(3,1),(4,2),(5,2),(6,2),(6,7),(7,3),(8,3),(9,3),(10,3),
(11,4),(12,4),(13,4),(14,5),(15,5),(16,6),(17,6),(18,7),(19,7),(19,4),(20,1),
(21,8),(22,8),(23,8),(24,9),(25,9),(26,9),(26,4),(27,10),(28,10),(29,10),
(30,8),(31,9),(32,10),(32,3),(33,8),(34,9),(34,8),(35,10),(35,4);

-- ===========================================================================
-- 6) USUARIO_TOPICO  (interesses: 3 a 5 topicos por usuario)
-- ===========================================================================
INSERT INTO usuario_topico (id_usuario, id_topico) VALUES
(1,1),(1,4),(1,5),(1,7),
(2,1),(2,2),(2,3),
(3,1),(3,2),(3,4),(3,5),
(4,3),(4,7),(4,9),
(5,4),(5,8),(5,10),
(6,1),(6,2),(6,3),(6,6),
(7,2),(7,6),(7,8),
(8,1),(8,4),(8,5),
(9,4),(9,7),(9,8),(9,9),
(10,1),(10,3),(10,9),
(11,4),(11,5),(11,8),(11,10),
(12,1),(12,2),(12,3),(12,7),(12,9);

-- ===========================================================================
-- 7) USUARIO_COMUNIDADE  (participacoes)
-- ===========================================================================
INSERT INTO usuario_comunidade (id_usuario, id_comunidade) VALUES
(1,1),(1,3),(1,4),
(2,1),(2,2),
(3,3),(3,4),
(4,2),(4,5),
(5,3),(5,5),
(6,1),(6,2),
(7,1),(7,4),
(8,1),(8,3),
(9,3),(9,5),
(10,1),(10,2),(10,5),
(11,3),(11,4),
(12,1),(12,2),(12,5);

-- ===========================================================================
-- 8) USUARIO_CONFIGURACAO  (preferencias de recomendacao/notificacao)
-- ===========================================================================
INSERT INTO usuario_configuracao (id_usuario, sugestao_saudavel_ativa, personalizacao_ativa, notificacao_foco_ativa) VALUES
(1,  TRUE,  TRUE,  TRUE),
(2,  TRUE,  TRUE,  FALSE),
(3,  TRUE,  FALSE, TRUE),
(4,  FALSE, TRUE,  TRUE),
(5,  TRUE,  TRUE,  TRUE),
(6,  TRUE,  TRUE,  TRUE),
(7,  TRUE,  TRUE,  FALSE),
(8,  TRUE,  FALSE, TRUE),
(9,  TRUE,  TRUE,  TRUE),
(10, FALSE, TRUE,  TRUE),
(11, TRUE,  TRUE,  TRUE),
(12, TRUE,  TRUE,  FALSE);

-- ===========================================================================
-- 9) META_DE_FOCO  (metas de foco por usuario; duracao em minutos)
-- ===========================================================================
INSERT INTO meta_de_foco (id_meta, usuario_associado_id, categoria, duracao_definida, status) VALUES
(1, 1,  'PRODUTIVIDADE',  90,  'ATIVA'),
(2, 2,  'PRODUTIVIDADE',  60,  'ATIVA'),
(3, 3,  'ENTRETENIMENTO', 30,  'PAUSADA'),
(4, 4,  'PRODUTIVIDADE',  45,  'CONCLUIDA'),
(5, 6,  'PRODUTIVIDADE',  120, 'ATIVA'),
(6, 8,  'ENTRETENIMENTO', 25,  'ATIVA'),
(7, 10, 'PRODUTIVIDADE',  50,  'CONCLUIDA'),
(8, 12, 'PRODUTIVIDADE',  90,  'ATIVA');

-- ===========================================================================
-- 10) SESSAO_DE_USO  (tempos em minutos; feedback_da_sessao entre 1 e 5)
--     Inclui sessoes com modo_absoluto = TRUE
-- ===========================================================================
INSERT INTO sessao_de_uso (id_sessao, usuario_associado_id, hora_inicio, hora_fim, tempo_produtividade_realizado, tempo_entretenimento_realizado, feedback_da_sessao, modo_absoluto) VALUES
(1, 1,  '2026-07-07 09:00:00', '2026-07-07 10:35:00', 85,  10, 5,    FALSE),
(2, 6,  '2026-07-07 14:00:00', '2026-07-07 15:55:00', 110, 5,  4,    TRUE),
(3, 4,  '2026-07-08 08:30:00', '2026-07-08 09:30:00', 45,  15, 4,    FALSE),
(4, 10, '2026-07-08 19:00:00', '2026-07-08 20:10:00', 50,  20, 3,    FALSE),
(5, 12, '2026-07-09 07:45:00', '2026-07-09 09:21:00', 88,  8,  5,    TRUE),
(6, 3,  '2026-07-09 21:10:00', NULL,                   20,  0,  NULL, FALSE);

-- ===========================================================================
-- 11) SESSAO_META  (liga sessoes as metas)
-- ===========================================================================
INSERT INTO sessao_meta (id_sessao, id_meta) VALUES
(1, 1),
(2, 5),
(3, 4),
(4, 7),
(5, 8),
(6, 3);

-- ===========================================================================
-- 12) FEEDBACK_CONTEUDO  (tipo: util | nao_relevante | relaxante)
--     UNIQUE (id_conteudo, id_usuario) - sem pares repetidos
-- ===========================================================================
INSERT INTO feedback_conteudo (id_feedback, id_conteudo, id_usuario, tipo) VALUES
(1,  1,  2,  'util'),
(2,  1,  3,  'relaxante'),
(3,  7,  4,  'util'),
(4,  7,  10, 'util'),
(5,  11, 3,  'relaxante'),
(6,  11, 8,  'relaxante'),
(7,  19, 1,  'util'),
(8,  19, 5,  'util'),
(9,  21, 5,  'relaxante'),
(10, 9,  6,  'util'),
(11, 9,  12, 'util'),
(12, 14, 1,  'util'),
(13, 18, 9,  'util'),
(14, 24, 4,  'util'),
(15, 27, 11, 'nao_relevante'),
(16, 33, 11, 'relaxante'),
(17, 13, 8,  'relaxante'),
(18, 2,  6,  'util'),
(19, 26, 9,  'util'),
(20, 35, 3,  'relaxante'),
(21, 3,  7,  'nao_relevante'),
(22, 16, 7,  'util');

-- ===========================================================================
-- 13) DENUNCIA  (moderacao de conteudo)
--     motivo: desinformacao|discurso_de_odio|assedio|violencia|fraude|outro
--     status: PENDENTE|EM_ANALISE|RESOLVIDA|REJEITADA
-- ===========================================================================
INSERT INTO denuncia (id_denuncia, id_conteudo, id_usuario, motivo, detalhes, status) VALUES
(1, 32, 5,  'outro',            'Algumas piadas podem soar excludentes para iniciantes na area.', 'PENDENTE'),
(2, 27, 8,  'discurso_de_odio', 'Parte dos memes contem linguagem que pode ofender grupos especificos.', 'EM_ANALISE'),
(3, 22, 11, 'desinformacao',    'Datas e nomes de bandas parecem imprecisos no texto.', 'REJEITADA');

-- ============================================================================
--  Fim do seed.
--  Contagens: 12 usuarios, 10 topicos, 5 comunidades, 35 conteudos,
--  41 linhas conteudo_topico, 43 usuario_topico, 27 usuario_comunidade,
--  12 usuario_configuracao, 8 metas, 6 sessoes, 6 sessao_meta,
--  22 feedbacks, 3 denuncias.
-- ============================================================================
