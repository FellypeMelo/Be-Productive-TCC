import random
from typing import List, Optional, TYPE_CHECKING
from src.application.interfaces import ContentRepositoryInterface, TrajectoryRepositoryInterface, ContentItem
from src.infrastructure.database import get_db_connection

if TYPE_CHECKING:
    from src.infrastructure.hybrid_scorer import HybridScorer

class MySQLContentRepository(ContentRepositoryInterface):
    """
    Adapter para o Repositório de Conteúdos, aplicando SRP.
    Converte queries MySQL sujas diretamente no DTO de Caso de Uso.
    Uses HybridRecommender for base_score when available.
    """
    def __init__(self, hybrid_scorer: Optional["HybridScorer"] = None):
        self._hybrid_scorer = hybrid_scorer

    def get_candidate_contents(
        self,
        category: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[ContentItem]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if user_id is not None:
            query = """
                SELECT DISTINCT c.id_conteudo, c.categoria
                FROM conteudo c
                JOIN conteudo_topico ct ON ct.id_conteudo = c.id_conteudo
                JOIN usuario_topico ut ON ut.id_topico = ct.id_topico AND ut.id_usuario = %s
            """
            params: list = [user_id]
            if category:
                query += " AND c.categoria = %s"
                params.append(category)
        else:
            query = "SELECT id_conteudo, categoria FROM conteudo"
            params = []
            if category:
                query += " WHERE categoria = %s"
                params.append(category)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Get model-based scores if scorer is available
        if self._hybrid_scorer is not None and user_id is not None:
            candidate_ids = [row["id_conteudo"] for row in rows]
            scores = self._hybrid_scorer.score_content_for_user(
                user_id=user_id, candidate_ids=candidate_ids, category=category
            )
        else:
            scores = None

        items = []
        for row in rows:
            base_score = scores.get(row["id_conteudo"], 0.5) if scores else random.uniform(0.3, 0.9)
            items.append(ContentItem(
                content_id=row["id_conteudo"],
                category=row["categoria"],
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

    def set_fatigue_alarm(self, user_id: int, is_fatigued: bool) -> None:
        if user_id not in self._store:
            self._store[user_id] = {"alarm": False}
        self._store[user_id]["alarm"] = is_fatigued

    def record_behavioral_event(self, user_id: int, v_scroll: float, v_alt: float) -> None:
        if user_id not in self._store:
            self._store[user_id] = {"alarm": False, "events": []}
        self._store[user_id].setdefault("events", []).append((v_scroll, v_alt))

    def get_recent_behavior(self, user_id: int, n: int = 10) -> list:
        data = self._store.get(user_id, {})
        events = data.get("events", [])
        return events[-n:]
