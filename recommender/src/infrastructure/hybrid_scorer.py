import hashlib
import math
from typing import Dict, List, Optional

from src.application.interfaces import ContentItem
from src.models.hybrid import HybridRecommender

# Bounds for the heuristic placeholder score used while the model is unfitted.
_HEURISTIC_MIN = 0.3
_HEURISTIC_MAX = 0.9

# Observable-ranker calibration. These values are deliberately centralized so
# an offline evaluation can tune them without changing the ranking flow.
_RECENCY_HALF_LIFE_HOURS = 24.0 * 14.0
_FEEDBACK_PRIOR_ALPHA = 2.0
_FEEDBACK_PRIOR_BETA = 2.0
_IMPLICIT_SKIP_WEIGHT = 0.10
_FEEDBACK_EVIDENCE_SCALE = 6.0

# Intent alignment and content quality carry 72% of the positive score. User
# reactions are useful but deliberately secondary: the objective is sustainable
# attention, not immediate engagement.
_AFFINITY_WEIGHT = 0.40
_QUALITY_WEIGHT = 0.32
_FEEDBACK_WEIGHT = 0.08
_RECENCY_WEIGHT = 0.07
_NOVELTY_WEIGHT = 0.08
_EXPLORATION_WEIGHT = 0.05


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


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _feedback_signal(
    positive_events: int,
    negative_events: int,
    impression_count: int,
) -> tuple[float, float, float]:
    """Return calibrated feedback, confidence, and explicit-negative rate.

    A Beta(2, 2) prior prevents one click from overwhelming quality and topic
    relevance. Impressions without a recorded reaction count as a weak skip,
    while explicit hides remain a much stronger negative signal. Confidence
    grows smoothly with evidence instead of switching behavior abruptly.
    """
    positive = max(0, int(positive_events))
    negative = max(0, int(negative_events))
    impressions = max(0, int(impression_count))
    implicit_skips = max(0, impressions - positive - negative)
    effective_negative = negative + _IMPLICIT_SKIP_WEIGHT * implicit_skips

    alpha = _FEEDBACK_PRIOR_ALPHA + positive
    beta = _FEEDBACK_PRIOR_BETA + effective_negative
    posterior = alpha / (alpha + beta)
    evidence = positive + negative + _IMPLICIT_SKIP_WEIGHT * implicit_skips
    confidence = 1.0 - math.exp(-evidence / _FEEDBACK_EVIDENCE_SCALE)
    calibrated = 0.5 + confidence * (posterior - 0.5)
    explicit_negative_rate = negative / max(1, positive + negative)
    return _clamp01(calibrated), _clamp01(confidence), explicit_negative_rate


def _attention_support(item: ContentItem) -> float:
    """Estimate whether an item can sustain deliberate attention.

    Quality is the dominant input. Textual depth is a small, saturating signal
    so concise high-quality audio/video descriptions are not excluded merely
    for having less text. This signal intentionally excludes clicks and dwell.
    """
    words = len(f"{item.title} {item.body}".split())
    depth = 1.0 - math.exp(-words / 120.0)
    return _clamp01(0.75 * _clamp01(item.quality_score) + 0.25 * depth)


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
            return {cid: _heuristic_content_score(cid) for cid in candidate_ids}

    def score_items_for_user(
        self,
        user_id: int,
        items: List[ContentItem],
    ) -> Dict[int, float]:
        """Rank from observed features without requiring a trained model.

        Sparse feedback is confidence-weighted against a neutral Bayesian
        prior. Recency uses a documented half-life, repeated exposure receives
        a bounded penalty, and exploration remains deterministic per
        user/content pair for reproducible A/B analysis.
        """
        scores: Dict[int, float] = {}
        for item in items:
            affinity = _clamp01(item.topic_affinity)
            quality = _clamp01(item.quality_score)
            age_hours = max(0.0, float(item.age_hours))
            recency = math.exp(
                -math.log(2.0) * age_hours / _RECENCY_HALF_LIFE_HOURS
            )
            impressions = max(0, int(item.impression_count))
            novelty = 1.0 / math.sqrt(1.0 + impressions)
            feedback, feedback_confidence, negative_rate = _feedback_signal(
                item.positive_events,
                item.negative_events,
                impressions,
            )
            digest = hashlib.sha256(
                f"explore:{user_id}:{item.content_id}".encode("utf-8")
            ).digest()
            exploration = int.from_bytes(digest[:8], "big") / float(2**64 - 1)

            repetition_penalty = min(
                0.18,
                0.12 * negative_rate * feedback_confidence
                + 0.06 * (1.0 - novelty),
            )
            score = (
                _AFFINITY_WEIGHT * affinity
                + _QUALITY_WEIGHT * quality
                + _FEEDBACK_WEIGHT * feedback
                + _RECENCY_WEIGHT * recency
                + _NOVELTY_WEIGHT * novelty
                + _EXPLORATION_WEIGHT * exploration
                - repetition_penalty
            )
            item.explanations = self._explain(
                item,
                recency=recency,
                feedback=feedback,
                feedback_confidence=feedback_confidence,
                novelty=novelty,
                repetition_penalty=repetition_penalty,
            )
            item.attention_support = _attention_support(item)
            scores[item.content_id] = _clamp01(score)
        return scores

    @staticmethod
    def _explain(
        item: ContentItem,
        *,
        recency: float,
        feedback: float,
        feedback_confidence: float,
        novelty: float,
        repetition_penalty: float,
    ) -> List[str]:
        reasons: List[str] = []
        if item.topic_affinity >= 0.5:
            reasons.append("matches_your_topics")
        if item.quality_score >= 0.7:
            reasons.append("high_quality")
        if feedback >= 0.65 and feedback_confidence >= 0.35:
            reasons.append("positive_history")
        if recency >= 0.8:
            reasons.append("recent")
        if novelty >= 0.7:
            reasons.append("not_repetitive")
        if item.negative_events > item.positive_events and feedback_confidence >= 0.35:
            reasons.append("negative_history_penalty")
        elif repetition_penalty >= 0.04:
            reasons.append("repetition_penalty")
        return reasons[:4] or ["balanced_candidate"]

    def get_quality_scores(self) -> Dict:
        return self._model._quality_cache
