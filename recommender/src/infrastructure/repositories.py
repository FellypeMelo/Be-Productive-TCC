import random
from typing import List, Optional
from src.application.interfaces import ContentRepositoryInterface, TrajectoryRepositoryInterface, ContentItem
from src.infrastructure.database import get_db_connection

class MySQLContentRepository(ContentRepositoryInterface):
    """
    Adapter para o Repositório de Conteúdos, aplicando SRP.
    Converte queries MySQL sujas diretamente no DTO de Caso de Uso.
    """
    def get_candidate_contents(self, category: Optional[str] = None) -> List[ContentItem]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT id_conteudo, categoria FROM conteudo"
        params = []
        
        if category:
            query += " WHERE categoria = %s"
            params.append(category)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        items = []
        for row in rows:
            # Random base_score since the real RS models (Hybrid/ContentBased) are placeholders
            # and our focus is architectural mapping of the Paper models
            base_score = random.uniform(0.3, 0.9)
            items.append(ContentItem(
                content_id=row['id_conteudo'],
                category=row['categoria'],
                base_score=base_score
            ))
            
        return items

class InMemoryTrajectoryRepository(TrajectoryRepositoryInterface):
    """
    Maneja os parâmetros de fadiga EDO (Eq 4).
    Em um cenário de mundo real, usa Redis ou MongoDB para rápida leitura.
    """
    def __init__(self):
        self._store = {}
        
    def save_fatigue_parameters(self, user_id: int, mu_rest: float, kappa1: float, kappa2: float) -> None:
        self._store[user_id] = {
            "mu_rest": mu_rest,
            "k1": kappa1,
            "k2": kappa2,
            "alarm": False # default state
        }
        
    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        # Puxa o status reportado pelo Edge AI (Simulated for now)
        data = self._store.get(user_id)
        if not data:
            return False
        return data.get("alarm", False)
