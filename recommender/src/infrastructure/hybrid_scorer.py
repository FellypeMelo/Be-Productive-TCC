from typing import List, Optional, Dict
import numpy as np

from src.models.hybrid import HybridRecommender


class HybridScorer:
    """
    Infrastructure adapter that wires the HybridRecommender model
    into the production recommendation pipeline.
    Replaces the random base_score with actual model-derived scores.
    """

    def __init__(self):
        self._model = HybridRecommender(
            content_weight=0.4,
            collab_weight=0.4,
            quality_weight=0.2
        )
        self._is_fitted = False

    def score_content_for_user(
        self,
        user_id: int,
        candidate_ids: List[int],
        category: Optional[str] = None
    ) -> Dict[int, float]:
        """
        Returns {content_id: base_score} for each candidate,
        using the hybrid model (TF-IDF + ALS + quality).
        """
        if not candidate_ids:
            return {}

        if not self._is_fitted:
            return {cid: 0.5 for cid in candidate_ids}

        try:
            _, scores = self._model.predict(
                user_id=user_id,
                candidate_ids=candidate_ids,
                category=category
            )
            return dict(zip(candidate_ids, scores.tolist()))
        except Exception:
            return {cid: 0.5 for cid in candidate_ids}

    def get_quality_scores(self) -> Dict:
        return self._model._quality_cache
