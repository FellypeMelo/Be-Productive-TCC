import random
import hashlib
import datetime

# Configuration
NUM_USERS = 50
NUM_TOPICS = 30
NUM_COMMUNITIES = 15
NUM_CONTENT = 200
NUM_FEEDBACK = 500
NUM_SESSIONS = 150
NUM_DENUNCIAS = 40

# Helper to hash password (must match backend's SHA256 logic)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Data Pools
NAMES = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Niaj", "Olivia", "Peggy", "Quentin", "Rupert", "Sybil", "Trent", "Victor", "Walter", "Arthur", "Beatrice", "Cyril", "Diana", "Edgar", "Flora", "George", "Helena", "Isidore", "Jane"]
SURNAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
TOPICS = [
    "Technology", "Productivity", "Mental Health", "Music", "Movies", "Gaming", "Reading", "Fitness", "Meditation", "Cooking",
    "Science", "History", "Art", "Design", "Photography", "Travel", "Fashion", "Sports", "Politics", "Economics",
    "Psychology", "Philosophy", "Space", "Nature", "Education", "Coding", "Startups", "Finance", "Yoga", "Mindfulness"
]
CONTENT_TITLES = [
    "10 Tips for Better Focus", "Why You Should Meditate", "Top 5 Movies of 2024", "Understanding Quantum Physics", "Healthy Recipes for Dinner",
    "Best Coding Practices", "How to Manage Stress", "The History of Rome", "Travel Guide to Japan", "Yoga for Beginners",
    "The Future of AI", "Deep Work Techniques", "Mastering Time Management", "Cognitive Behavioral Therapy Intro", "Exploring the Solar System",
    "Gourmet Coffee at Home", "Sustainable Living Tips", "Minimalist Living", "Learning a New Language", "The Power of Habit"
]

def generate_sql():
    sql = []
    sql.append("-- Comprehensive Mock Data Seed with Media URLs")
    sql.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql.append("TRUNCATE TABLE usuario_configuracao;")
    sql.append("TRUNCATE TABLE usuario_comunidade;")
    sql.append("TRUNCATE TABLE usuario_topico;")
    sql.append("TRUNCATE TABLE conteudo_topico;")
    sql.append("TRUNCATE TABLE sessao_meta;")
    sql.append("TRUNCATE TABLE feedback_conteudo;")
    sql.append("TRUNCATE TABLE denuncia;")
    sql.append("TRUNCATE TABLE sessao_de_uso;")
    sql.append("TRUNCATE TABLE meta_de_foco;")
    sql.append("TRUNCATE TABLE conteudo;")
    sql.append("TRUNCATE TABLE comunidade;")
    sql.append("TRUNCATE TABLE topico;")
    sql.append("TRUNCATE TABLE usuario;")
    sql.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql.append("")

    # 1. Users
    users = []
    print("Generating Users...")
    for i in range(1, NUM_USERS + 1):
        name = f"{random.choice(NAMES)} {random.choice(SURNAMES)}"
        email = f"user{i}@example.com"
        password = "password123"
        hashed = hash_password(password)
        state = random.choice(['NEUTRO', 'POSITIVO', 'NEGATIVO', 'ESTRESSADO'])
        users.append(f"({i}, '{name}', '{email}', '{hashed}', '{state}')")
    
    sql.append(f"INSERT INTO usuario (id_usuario, nome, email, senha_criptografada, estado_emocional_inferido) VALUES")
    sql.append(",\n".join(users) + ";")
    sql.append("")

    # 2. User Configurations
    user_configs = []
    print("Generating User Configurations...")
    for i in range(1, NUM_USERS + 1):
        sug = 'TRUE' if random.random() > 0.2 else 'FALSE'
        pers = 'TRUE' if random.random() > 0.1 else 'FALSE'
        notif = 'TRUE' if random.random() > 0.15 else 'FALSE'
        user_configs.append(f"({i}, {sug}, {pers}, {notif})")
    
    sql.append(f"INSERT INTO usuario_configuracao (id_usuario, sugestao_saudavel_ativa, personalizacao_ativa, notificacao_foco_ativa) VALUES")
    sql.append(",\n".join(user_configs) + ";")
    sql.append("")

    # 3. Topics
    topics = []
    print("Generating Topics...")
    for i, topic_name in enumerate(TOPICS, start=1):
        desc = f"Learn more about {topic_name} and how it impacts your life."
        topics.append(f"({i}, '{topic_name}', '{desc}')")

    sql.append(f"INSERT INTO topico (id_topico, nome_topico, descricao) VALUES")
    sql.append(",\n".join(topics) + ";")
    sql.append("")

    # 4. Communities
    communities = []
    print("Generating Communities...")
    for i in range(1, NUM_COMMUNITIES + 1):
        name = f"Community of {random.choice(TOPICS)} {i}"
        topic_id = random.randint(1, NUM_TOPICS)
        rules = "1. Be respectful. 2. Share quality content. 3. No spam."
        communities.append(f"({i}, '{name}', {topic_id}, '{rules}')")
    
    sql.append(f"INSERT INTO comunidade (id_comunidade, nome_comunidade, topico_principal_id, regras_de_moderacao) VALUES")
    sql.append(",\n".join(communities) + ";")
    sql.append("")

    # 5. User-Community relationship
    user_communities = []
    print("Generating User-Communities...")
    seen_uc = set()
    for user_id in range(1, NUM_USERS + 1):
        num_comm = random.randint(1, 4)
        selected_comm = random.sample(range(1, NUM_COMMUNITIES + 1), num_comm)
        for comm_id in selected_comm:
            if (user_id, comm_id) not in seen_uc:
                user_communities.append(f"({user_id}, {comm_id})")
                seen_uc.add((user_id, comm_id))
    
    sql.append(f"INSERT INTO usuario_comunidade (id_usuario, id_comunidade) VALUES")
    sql.append(",\n".join(user_communities) + ";")
    sql.append("")

    # 6. User-Topics
    user_topics = []
    print("Generating User-Topics...")
    seen_ut = set()
    for user_id in range(1, NUM_USERS + 1):
        num_topics = random.randint(3, 5)
        selected_topics = random.sample(range(1, NUM_TOPICS + 1), num_topics)
        for topic_id in selected_topics:
            if (user_id, topic_id) not in seen_ut:
                user_topics.append(f"({user_id}, {topic_id})")
                seen_ut.add((user_id, topic_id))
    
    sql.append(f"INSERT INTO usuario_topico (id_usuario, id_topico) VALUES")
    sql.append(",\n".join(user_topics) + ";")
    sql.append("")

    # 7. Content
    content_list = []
    print("Generating Content...")
    for i in range(1, NUM_CONTENT + 1):
        title = f"{random.choice(CONTENT_TITLES)} #{i}"
        body = "This is a detailed article/post about personal growth, productivity and maintaining a healthy state of mind in the digital age."
        media_type = random.choice(['TEXTO', 'VIDEO', 'AUDIO'])
        
        midia_url = "NULL"
        if media_type == 'VIDEO':
            midia_url = "'https://www.youtube.com/embed/dQw4w9WgXcQ'"
        elif media_type == 'AUDIO':
            midia_url = "'https://w.soundcloud.com/player/?url=https://api.soundcloud.com/tracks/293'"

        category = random.choice(['PRODUTIVIDADE', 'ENTRETENIMENTO'])
        autor_id = random.randint(1, NUM_USERS)
        date = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')
        score = round(random.uniform(0.1, 1.0), 4)
        tags = f"{random.choice(TOPICS)},{random.choice(TOPICS)}"

        content_list.append(f"({i}, '{title}', '{body}', {midia_url}, '{media_type}', '{category}', {autor_id}, '{date}', '{tags}', {score})")

    sql.append(f"INSERT INTO conteudo (id_conteudo, titulo, corpo, midia_url, tipo_de_midia, categoria, autor_id, data_publicacao, tags_relevantes, score_de_qualidade) VALUES")
    sql.append(",\n".join(content_list) + ";")
    sql.append("")

    # 8. Content-Topic relationship
    content_topics = []
    print("Generating Content-Topics...")
    seen_ct = set()
    for content_id in range(1, NUM_CONTENT + 1):
        num_topics = random.randint(1, 3)
        selected_topics = random.sample(range(1, NUM_TOPICS + 1), num_topics)
        for topic_id in selected_topics:
            if (content_id, topic_id) not in seen_ct:
                content_topics.append(f"({content_id}, {topic_id})")
                seen_ct.add((content_id, topic_id))
    
    sql.append(f"INSERT INTO conteudo_topico (id_conteudo, id_topico) VALUES")
    sql.append(",\n".join(content_topics) + ";")
    sql.append("")

    # 9. Feedback
    feedbacks = []
    print("Generating Feedback...")
    seen_feed = set()
    feedback_id = 1
    while len(feedbacks) < NUM_FEEDBACK:
        user_id = random.randint(1, NUM_USERS)
        content_id = random.randint(1, NUM_CONTENT)
        if (user_id, content_id) not in seen_feed:
            seen_feed.add((user_id, content_id))
            type_ = random.choice(['util', 'nao_relevante', 'relaxante'])
            feedbacks.append(f"({feedback_id}, {content_id}, {user_id}, '{type_}')")
            feedback_id += 1

    sql.append(f"INSERT INTO feedback_conteudo (id_feedback, id_conteudo, id_usuario, tipo) VALUES")
    sql.append(",\n".join(feedbacks) + ";")
    sql.append("")

    # 10. Denuncias (Reports)
    denuncias = []
    print("Generating Denuncias...")
    for i in range(1, NUM_DENUNCIAS + 1):
        content_id = random.randint(1, NUM_CONTENT)
        user_id = random.randint(1, NUM_USERS)
        motivo = random.choice(['desinformacao', 'discurso_de_odio', 'assedio', 'violencia', 'fraude', 'outro'])
        detalhes = "Reporting this content due to policy violation."
        status = random.choice(['PENDENTE', 'EM_ANALISE', 'RESOLVIDA', 'REJEITADA'])
        denuncias.append(f"({i}, {content_id}, {user_id}, '{motivo}', '{detalhes}', '{status}')")
    
    sql.append(f"INSERT INTO denuncia (id_denuncia, id_conteudo, id_usuario, motivo, detalhes, status) VALUES")
    sql.append(",\n".join(denuncias) + ";")
    sql.append("")

    # 11. Focus Goals
    goals = []
    print("Generating Focus Goals...")
    for i in range(1, 101):
        user_id = random.randint(1, NUM_USERS)
        cat = random.choice(['PRODUTIVIDADE', 'ENTRETENIMENTO'])
        dur = random.choice([15, 25, 30, 45, 60, 90])
        stat = random.choice(['ATIVA', 'PAUSADA', 'CONCLUIDA'])
        goals.append(f"({i}, {user_id}, '{cat}', {dur}, '{stat}')")
    
    sql.append(f"INSERT INTO meta_de_foco (id_meta, usuario_associado_id, categoria, duracao_definida, status) VALUES")
    sql.append(",\n".join(goals) + ";")
    sql.append("")

    # 12. Focus Sessions
    sessions = []
    print("Generating Focus Sessions...")
    for i in range(1, NUM_SESSIONS + 1):
        user_id = random.randint(1, NUM_USERS)
        start = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        duration_prod = random.randint(10, 60)
        duration_ent = random.randint(5, 20)
        end = start + datetime.timedelta(minutes=duration_prod + duration_ent)
        
        start_str = start.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end.strftime('%Y-%m-%d %H:%M:%S')
        feedback_sessao = random.randint(1, 5)
        modo_abs = 'TRUE' if random.random() > 0.7 else 'FALSE'

        sessions.append(f"({i}, {user_id}, '{start_str}', '{end_str}', {duration_prod}, {duration_ent}, {feedback_sessao}, {modo_abs})")

    sql.append(f"INSERT INTO sessao_de_uso (id_sessao, usuario_associado_id, hora_inicio, hora_fim, tempo_produtividade_realizado, tempo_entretenimento_realizado, feedback_da_sessao, modo_absoluto) VALUES")
    sql.append(",\n".join(sessions) + ";")
    sql.append("")

    # 13. Session-Goal relationship
    sessao_meta = []
    print("Generating Session-Meta...")
    for i in range(1, NUM_SESSIONS + 1):
        goal_id = random.randint(1, 100)
        sessao_meta.append(f"({i}, {goal_id})")
    
    sql.append(f"INSERT INTO sessao_meta (id_sessao, id_meta) VALUES")
    sql.append(",\n".join(sessao_meta) + ";")
    
    return "\n".join(sql)

if __name__ == "__main__":
    sql_content = generate_sql()
    import os
    target_path = os.path.join(os.path.dirname(__file__), "mock_data.sql")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
    print(f"Successfully generated {target_path}")
