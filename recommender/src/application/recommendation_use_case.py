from typing import List, Optional
from src.application.interfaces import (
    ContentRepositoryInterface,
    SafetyClassifierInterface,
    HawkesClassifierInterface,
    ContentItem,
)
from src.domain.math_models import calculate_quality_score, thompson_sampling_choice


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
    ) -> List[ContentItem]:
        candidates = self.repo.get_candidate_contents(user_id=user_id)

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
            probs = self.safety_classifier.infer_safety_probabilities(item.content_id)
            quality = calculate_quality_score(item.base_score, probs)

            score = quality.value

            # Hawkes-informed penalty/boost
            if hawkes_result is not None:
                ratio = hawkes_result["ratio"]  # lambda_s1 / lambda_s2
                # If user is in System 1 mode (ratio > 2), penalize ENTRETENIMENTO
                # to prevent doom-scrolling cascade
                if ratio > 2.0 and item.category == "ENTRETENIMENTO":
                    score *= 0.5  # 50% penalty for entertainment during impulsive state
                # If user is in System 2 mode (ratio < 0.5), boost PRODUTIVIDADE
                elif ratio < 0.5 and item.category == "PRODUTIVIDADE":
                    score *= 1.2  # 20% boost for productivity during deliberative state

            item.perceived_value = max(0.0, min(1.0, score))
            item.base_score = score

        valid_items = [i for i in candidates if i.perceived_value > 0.0]
        valid_items.sort(key=lambda x: x.perceived_value, reverse=True)

        return valid_items[:limit]

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
