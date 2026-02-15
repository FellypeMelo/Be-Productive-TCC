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

def get_all_content_ids(category=None):
    """Fetch all available content IDs from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT id_conteudo FROM conteudo"
    params = []
    if category:
        query += " WHERE categoria = %s"
        params.append(category)
        
    cursor.execute(query, params)
    ids = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return ids
