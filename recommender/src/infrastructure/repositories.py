from typing import List, Optional, TYPE_CHECKING
from src.application.interfaces import ContentRepositoryInterface, ContentItem
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
        user_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> List[ContentItem]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT c.id_conteudo, c.categoria, c.titulo, c.corpo,
                   COALESCE(c.tags_relevantes, '') AS tags_relevantes,
                   CAST(c.score_de_qualidade AS DOUBLE) AS quality_score,
                   GREATEST(0, TIMESTAMPDIFF(HOUR, c.data_publicacao, NOW())) AS age_hours,
                   CASE WHEN EXISTS (
                       SELECT 1 FROM conteudo_topico ct
                       JOIN usuario_topico ut ON ut.id_topico = ct.id_topico
                       WHERE ct.id_conteudo = c.id_conteudo AND ut.id_usuario = %s
                   ) THEN 1.0 ELSE 0.0 END AS topic_affinity,
                   COALESCE(events.positive_events, 0) AS positive_events,
                   COALESCE(events.negative_events, 0) AS negative_events,
                   COALESCE(events.impression_count, 0) AS impression_count
            FROM conteudo c
            LEFT JOIN (
                SELECT id_conteudo,
                       SUM(tipo IN ('open', 'complete')) AS positive_events,
                       SUM(tipo = 'hide') AS negative_events,
                       SUM(tipo = 'impression') AS impression_count
                FROM interacao_conteudo WHERE id_usuario = %s GROUP BY id_conteudo
            ) events ON events.id_conteudo = c.id_conteudo
            WHERE (%s IS NULL OR c.categoria = %s)
              AND (%s IS NULL OR EXISTS (
                  SELECT 1 FROM conteudo_topico filter_topic
                  WHERE filter_topic.id_conteudo = c.id_conteudo AND filter_topic.id_topico = %s
              ))
            ORDER BY topic_affinity DESC, c.score_de_qualidade DESC, c.data_publicacao DESC
            LIMIT 500
        """
        effective_user_id = user_id or 0
        params = [effective_user_id, effective_user_id, category, category, topic_id, topic_id]

        cursor.execute(query, params)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        items: List[ContentItem] = []
        for row in rows:
            items.append(ContentItem(
                content_id=row["id_conteudo"],
                category=row["categoria"],
                base_score=float(row["quality_score"]),
                title=row["titulo"], body=row["corpo"], tags=row["tags_relevantes"],
                quality_score=float(row["quality_score"]),
                topic_affinity=float(row["topic_affinity"]),
                age_hours=float(row["age_hours"]),
                positive_events=int(row["positive_events"]),
                negative_events=int(row["negative_events"]),
                impression_count=int(row["impression_count"]),
            ))

        if self._hybrid_scorer is not None:
            scores = self._hybrid_scorer.score_items_for_user(effective_user_id, items)
            for item in items:
                item.base_score = scores[item.content_id]

        return items
