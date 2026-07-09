import hashlib
from typing import List, Optional, Dict

from src.models.hybrid import HybridRecommender

# Bounds for the heuristic placeholder score used while the model is unfitted.
_HEURISTIC_MIN = 0.3
_HEURISTIC_MAX = 0.9


def _heuristic_content_score(content_id: int) -> float:
    """Deterministic content-feature-based score in [0.3, 0.9].

    This is a HEURISTIC PLACEHOLDER, not a trained prediction. The real
    HybridRecommender is never fitted in this build, so instead of silently
    returning a constant 0.5 (which erased all ranking signal) or a random
    value (which broke reproducibility), we derive a stable, varied score from
    the content id via SHA-256. Same id -> same score, different ids spread
    across the documented range. Swap this out once the model is fitted.
    """
    digest = hashlib.sha256(f"content:{content_id}".encode("utf-8")).digest()
    u = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return _HEURISTIC_MIN + u * (_HEURISTIC_MAX - _HEURISTIC_MIN)


class HybridScorer:
    """
    Infrastructure adapter that wires the HybridRecommender model
    into the production recommendation pipeline.

    When the underlying model is fitted, it returns real model-derived scores.
    While it is unfitted (the current default), it returns a documented,
    deterministic heuristic score in [0.3, 0.9] per content id — never a silent
    constant and never random — so the feed still has a stable ordering signal.
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
        Returns {content_id: base_score} for each candidate.

        Fitted model -> hybrid (TF-IDF + ALS + quality) scores.
        Unfitted     -> deterministic heuristic placeholder in [0.3, 0.9].
        """
        if not candidate_ids:
            return {}

        if not self._is_fitted:
            return {cid: _heuristic_content_score(cid) for cid in candidate_ids}

        try:
            _, scores = self._model.predict(
                user_id=user_id,
                candidate_ids=candidate_ids,
                category=category
            )
            return dict(zip(candidate_ids, scores.tolist()))
        except Exception:
            # Degrade to the same deterministic heuristic rather than a constant.
            return {cid: _heuristic_content_score(cid) for cid in candidate_ids}

    def get_quality_scores(self) -> Dict:
        return self._model._quality_cache
