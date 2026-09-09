import math
from typing import List, Optional
from collections import Counter
from src.application.interfaces import (
    ContentRepositoryInterface,
    SafetyClassifierInterface,
    HawkesClassifierInterface,
    ContentItem,
)
from src.domain.math_models import calculate_quality_score, thompson_sampling_choice
from src.application.experiments import stable_variant


_PROTECTIVE_DENSITY_THRESHOLD = 0.55


class RecommendationUseCase:
    def __init__(
        self,
        repo: ContentRepositoryInterface,
        safety_clf: SafetyClassifierInterface,
        hawkes_clf: HawkesClassifierInterface,
    ):
        self.repo = repo
        self.safety_classifier = safety_clf
        self.hawkes_classifier = hawkes_clf
        # Thompson Sampling hyperparameters (paper Eq. 2)
        self._ts_alpha_s2 = 10.0
        self._ts_beta_s2 = 1.0
        # Per-user behavioral history: user_id -> list of event intervals (seconds)
        self._user_events: dict[int, list[float]] = {}

    def generate_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        absolute_mode_active: bool = False,
        declared_goal: Optional[str] = None,
        category: Optional[str] = None,
        topic_id: Optional[int] = None,
        protective_mode_active: bool = False,
        research_consent: bool = False,
    ) -> List[ContentItem]:
        if topic_id is None:
            candidates = self.repo.get_candidate_contents(user_id=user_id, category=category)
        else:
            candidates = self.repo.get_candidate_contents(
                user_id=user_id, category=category, topic_id=topic_id
            )
        experiment_variant = stable_variant(user_id, research_consent)

        # Hawkes classification based on user's recent behavior
        hawkes_result = None
        event_intervals = self._user_events.get(user_id, [])
        if len(event_intervals) >= 2:
            hawkes_result = self.hawkes_classifier.classify(event_intervals)

        for item in candidates:
            # Algorithm 4: Absolute Mode
            if absolute_mode_active and item.category != declared_goal:
                item.perceived_value = 0.0
                continue

            # Eq. 3: Min-Norm Safety Aggregation
            probs = self.safety_classifier.infer_content_probabilities(item)
            quality = calculate_quality_score(item.base_score, probs)

            score = quality.value

            # A privacy-preserving binary order from the on-device fatigue
            # engine. In this state the feed admits only content with enough
            # quality/depth to support deliberate attention. No raw behavioral
            # signal is needed by the server.
            if protective_mode_active:
                attention_support = self._attention_support(item)
                item.attention_support = attention_support
                if attention_support < _PROTECTIVE_DENSITY_THRESHOLD:
                    item.perceived_value = 0.0
                    item.explanations = ["filtered_by_protective_mode"]
                    continue
                score *= 0.75 + 0.25 * attention_support
                item.explanations.append("protective_dense_content")

            # Hawkes-informed penalty/boost
            if hawkes_result is not None:
                ratio = hawkes_result["ratio"]  # lambda_s1 / lambda_s2
                # If user is in System 1 mode (ratio > 2), penalize ENTRETENIMENTO
                # to prevent doom-scrolling cascade
                if ratio > 2.0 and item.category == "ENTRETENIMENTO":
                    score *= 0.5  # 50% penalty for entertainment during impulsive state
                    item.explanations.append("impulsive_state_penalty")
                # If user is in System 2 mode (ratio < 0.5), boost PRODUTIVIDADE
                elif ratio < 0.5 and item.category == "PRODUTIVIDADE":
                    score *= 1.2  # 20% boost for productivity during deliberative state
                    item.explanations.append("deliberative_state_boost")

            item.perceived_value = max(0.0, min(1.0, score))
            item.base_score = score

            highest_risk = max(p.value for p in probs) if probs else 0.0
            if highest_risk >= 0.95:
                item.perceived_value = 0.0
                item.explanations = ["blocked_by_safety"]
            elif highest_risk >= 0.5:
                item.explanations.append("safety_penalty")

        valid_items = [i for i in candidates if i.perceived_value > 0.0]
        valid_items.sort(key=lambda x: x.perceived_value, reverse=True)

        if experiment_variant == "treatment":
            valid_items = self._diversify(valid_items)

        return valid_items[:limit]

    @staticmethod
    def _attention_support(item: ContentItem) -> float:
        """Quality-led density score independent from engagement signals."""
        quality = min(1.0, max(0.0, float(item.quality_score)))
        words = len(f"{item.title} {item.body}".split())
        depth = 1.0 - math.exp(-words / 120.0)
        return min(1.0, max(0.0, 0.75 * quality + 0.25 * depth))

    @staticmethod
    def _diversify(items: List[ContentItem]) -> List[ContentItem]:
        """Greedy exposure-aware diversity with bounded relevance loss.

        Candidates more than eight score points below the best remaining item
        are never promoted. Within that relevance window, categories already
        exposed in the result receive a cumulative penalty. This avoids long
        same-category runs without letting diversity swamp relevance.
        """
        remaining = list(items)
        ranked: List[ContentItem] = []
        category_exposure: Counter[str] = Counter()
        while remaining:
            relevance_best = max(
                remaining,
                key=lambda item: (item.perceived_value, -item.content_id),
            )
            relevance_floor = relevance_best.perceived_value - 0.08
            eligible = [
                item for item in remaining
                if item.perceived_value >= relevance_floor
            ]
            best = max(
                eligible,
                key=lambda item: (
                    item.perceived_value - 0.05 * category_exposure[item.category],
                    -category_exposure[item.category],
                    item.perceived_value,
                    -item.content_id,
                ),
            )
            if best is not relevance_best:
                best.explanations.append("diversity_rerank")
            ranked.append(best)
            category_exposure[best.category] += 1
            remaining.remove(best)
        return ranked

    def should_explore_deliberative(self, user_id: int) -> bool:
        """
        Thompson Sampling choice between S1 (impulsive) and S2 (deliberative).
        Paper Eq. 2: biased toward S2 via alpha_s2=10, beta_s2=1.
        Returns True if S2 is selected (explore deliberative path).
        """
        result = thompson_sampling_choice(
            alpha_s1=self._ts_beta_s2,  # S1 arm (inverse)
            beta_s1=self._ts_alpha_s2,
            alpha_s2=self._ts_alpha_s2,  # S2 arm (biased toward deliberative)
            beta_s2=self._ts_beta_s2,
        )
        return result == 1
