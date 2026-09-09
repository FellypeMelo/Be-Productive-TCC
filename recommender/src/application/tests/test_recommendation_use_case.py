import pytest
from src.application.interfaces import (
    ContentItem,
    ContentRepositoryInterface,
    SafetyClassifierInterface,
    HawkesClassifierInterface,
)
from src.domain.value_objects import SafetyProbability
from src.application.recommendation_use_case import RecommendationUseCase
from src.domain.math_models import thompson_sampling_choice, calculate_hawkes_activation, calculate_quality_score


class MockContentRepo(ContentRepositoryInterface):
    def get_candidate_contents(self, category=None, user_id=None, topic_id=None):
        return [
            ContentItem(1, "PRODUTIVIDADE", 0.8),
            ContentItem(2, "ENTRETENIMENTO", 0.9),
            ContentItem(3, "PRODUTIVIDADE", 0.5)
        ]

class MockSafetyClassifier(SafetyClassifierInterface):
    def infer_safety_probabilities(self, content_id):
        if content_id == 2:
            return [
                SafetyProbability(0.9), SafetyProbability(0.8),
                SafetyProbability(0.1), SafetyProbability(0.1), SafetyProbability(0.1),
            ]
        return [
            SafetyProbability(0.1), SafetyProbability(0.05),
            SafetyProbability(0.05), SafetyProbability(0.05), SafetyProbability(0.05),
        ]


class MockHawkesClassifier(HawkesClassifierInterface):
    def __init__(self, ratio: float = 1.0):
        self._ratio = ratio

    def classify(self, event_intervals):
        return {
            "system": 1 if self._ratio > 1.0 else 2,
            "ratio": self._ratio,
            "lambda_s1": self._ratio,
            "lambda_s2": 1.0,
        }


def _make_use_case(hawkes_ratio: float = 1.0):
    repo = MockContentRepo()
    safety = MockSafetyClassifier()
    hawkes = MockHawkesClassifier(ratio=hawkes_ratio)
    return RecommendationUseCase(repo, safety, hawkes)


def test_recommendation_applies_min_aggregation_penalty():
    """Tests min-norm penalty: Item 2 toxic -> re-ordered below Item 1."""
    use_case = _make_use_case()
    recommendations = use_case.generate_recommendations(user_id=1, limit=3)

    assert recommendations[0].content_id == 1
    assert recommendations[2].content_id == 2


def test_absolute_mode_blinds_out_of_category_content():
    """Algoritmo 4: zero perceived value for out-of-category items."""
    use_case = _make_use_case()
    recommendations = use_case.generate_recommendations(
        user_id=1,
        limit=3,
        absolute_mode_active=True,
        declared_goal="PRODUTIVIDADE",
    )
    for rec in recommendations:
        if rec.category != "PRODUTIVIDADE":
            assert rec.perceived_value == 0.0
    assert all(rec.category == "PRODUTIVIDADE" for rec in recommendations if rec.perceived_value > 0)


def test_should_explore_deliberative_returns_bool():
    """Verify should_explore_deliberative returns a bool."""
    use_case = _make_use_case()
    result = use_case.should_explore_deliberative(user_id=1)
    assert isinstance(result, bool)


def test_thompson_biased_towards_s2_over_many_trials():
    """alpha_s2=10, beta_s2=1 biases toward S2; should win >60% of 100 trials."""
    use_case = _make_use_case()
    s2_wins = sum(1 for _ in range(100) if use_case.should_explore_deliberative(user_id=1))
    assert s2_wins > 60, f"Expected >60% S2, got {s2_wins}%"


def test_thompson_sampling_biased_towards_system2():
    """Direct test of thompson_sampling_choice function."""
    s2_wins = 0
    for _ in range(100):
        result = thompson_sampling_choice(
            alpha_s1=1.0, beta_s1=10.0,
            alpha_s2=10.0, beta_s2=1.0,
        )
        if result == 1:
            s2_wins += 1
    assert s2_wins > 60, f"Expected >60% S2, got {s2_wins}%"


def test_hawkes_penalizes_entertainment_during_impulsive_state():
    """When ratio > 2.0 (System 1), ENTRETENIMENTO score should be halved."""
    use_case = _make_use_case(hawkes_ratio=3.0)
    use_case._user_events[1] = [1.0, 1.5, 2.0, 0.5]  # short intervals = impulsive

    recs = use_case.generate_recommendations(user_id=1, limit=5)
    for rec in recs:
        if rec.category == "ENTRETENIMENTO":
            assert rec.perceived_value < 0.10, f"Expected <0.10 for entertainment, got {rec.perceived_value}"
            assert "impulsive_state_penalty" in rec.explanations


def test_diversity_uses_cumulative_category_exposure():
    items = [
        ContentItem(1, "PRODUTIVIDADE", 0.90),
        ContentItem(2, "PRODUTIVIDADE", 0.88),
        ContentItem(3, "ENTRETENIMENTO", 0.86),
    ]
    for item in items:
        item.perceived_value = item.base_score

    ranked = RecommendationUseCase._diversify(items)

    assert [item.content_id for item in ranked] == [1, 3, 2]
    assert "diversity_rerank" in ranked[1].explanations


def test_diversity_never_promotes_large_relevance_loss():
    items = [
        ContentItem(1, "PRODUTIVIDADE", 0.90),
        ContentItem(2, "PRODUTIVIDADE", 0.88),
        ContentItem(3, "ENTRETENIMENTO", 0.70),
    ]
    for item in items:
        item.perceived_value = item.base_score

    ranked = RecommendationUseCase._diversify(items)

    assert [item.content_id for item in ranked[:2]] == [1, 2]


def test_protective_mode_keeps_only_attention_supporting_content():
    class ProtectiveRepo(ContentRepositoryInterface):
        def get_candidate_contents(self, category=None, user_id=None, topic_id=None):
            return [
                ContentItem(
                    10, "ENTRETENIMENTO", 0.95,
                    title="Clique agora", body="Surpresa!", quality_score=0.35,
                ),
                ContentItem(
                    20, "ENTRETENIMENTO", 0.82,
                    title="Ensaio sobre cinema lento",
                    body=" ".join(["análise"] * 180),
                    quality_score=0.9,
                ),
            ]

    use_case = RecommendationUseCase(
        ProtectiveRepo(), MockSafetyClassifier(), MockHawkesClassifier()
    )

    recommendations = use_case.generate_recommendations(
        user_id=1, limit=10, protective_mode_active=True
    )

    assert [item.content_id for item in recommendations] == [20]
    assert "protective_dense_content" in recommendations[0].explanations


def test_protective_mode_can_return_an_empty_feed():
    class ShallowRepo(ContentRepositoryInterface):
        def get_candidate_contents(self, category=None, user_id=None, topic_id=None):
            return [ContentItem(10, "ENTRETENIMENTO", 0.95, quality_score=0.2)]

    use_case = RecommendationUseCase(
        ShallowRepo(), MockSafetyClassifier(), MockHawkesClassifier()
    )

    recommendations = use_case.generate_recommendations(
        user_id=1, protective_mode_active=True
    )

    assert recommendations == []


# ---- Quality score edge cases ----

def test_score_with_single_safety_flag_05():
    """Single safety flag at 0.5 -> score halved."""
    result = calculate_quality_score(0.8, [SafetyProbability(0.5)])
    assert result.value == pytest.approx(0.4, abs=0.001)


def test_score_with_all_zero_risk():
    """All safety probabilities at 0: no penalty applied."""
    result = calculate_quality_score(0.9, [SafetyProbability(0.0)] * 5)
    assert result.value == pytest.approx(0.9, abs=0.001)


def test_score_with_flag_at_one():
    """Flag at P=1.0 -> penalty factor = 0 -> score = 0."""
    result = calculate_quality_score(0.95, [SafetyProbability(1.0), SafetyProbability(0.0)])
    assert result.value == pytest.approx(0.0)


# ---- Hawkes activation ----

def test_hawkes_activation_decays():
    """Activation should decay exponentially over time."""
    t0 = calculate_hawkes_activation(1.0, 0.1, 0.0)
    assert t0 == pytest.approx(1.0)

    t10 = calculate_hawkes_activation(1.0, 0.1, 10.0)
    assert t10 == pytest.approx(0.3679, abs=0.001)


def test_hawkes_high_beta_decays_faster():
    """Higher beta means faster decay of activation."""
    low_beta = calculate_hawkes_activation(1.0, 0.01, 5.0)
    high_beta = calculate_hawkes_activation(1.0, 0.5, 5.0)
    assert high_beta < low_beta


# ---- Thompson Sampling edges ----

def test_thompson_sampling_returns_valid_arm_index():
    """Return value must always be 0 or 1."""
    for _ in range(50):
        arm = thompson_sampling_choice(1.0, 1.0, 1.0, 1.0)
        assert arm in (0, 1)


def test_thompson_biased_with_strong_s1_prior():
    """With strong S1 priors, S1 should dominate sampling."""
    s1_wins = sum(1 for _ in range(100)
                  if thompson_sampling_choice(100.0, 1.0, 1.0, 100.0) == 0)
    assert s1_wins > 90
