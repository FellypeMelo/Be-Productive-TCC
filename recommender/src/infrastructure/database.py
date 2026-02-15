import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get a connection to the MySQL database (KISS: Simple connection)"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "be_productive")
    )

def get_all_content_ids(category=None, topic_id=None):
    """Fetch available content IDs from the database with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT c.id_conteudo FROM conteudo c"
    params = []
    
    if topic_id:
        query += " INNER JOIN conteudo_topico ct ON c.id_conteudo = ct.id_conteudo"
        
    where_clauses = []
    if category:
        where_clauses.append("c.categoria = %s")
        params.append(category)
    if topic_id:
        where_clauses.append("ct.id_topico = %s")
        params.append(topic_id)
        
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    cursor.execute(query, params)
    ids = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return ids
