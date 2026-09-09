import pytest
from src.infrastructure.hybrid_scorer import HybridScorer, _feedback_signal
from src.application.interfaces import ContentItem


def test_unfitted_scores_are_in_documented_range():
    """Unfitted scorer returns a heuristic placeholder in [0.3, 0.9], not 0.5."""
    scorer = HybridScorer()
    scores = scorer.score_content_for_user(user_id=1, candidate_ids=[10, 20, 30])

    assert set(scores.keys()) == {10, 20, 30}
    for value in scores.values():
        assert 0.3 <= value <= 0.9


def test_unfitted_scores_are_varied():
    """Different content ids should produce different (non-constant) scores."""
    scorer = HybridScorer()
    scores = scorer.score_content_for_user(
        user_id=1, candidate_ids=[10, 20, 30, 40, 50]
    )
    # No longer a dead constant (previously every candidate scored 0.5).
    assert len(set(scores.values())) > 1
    assert scores != {cid: 0.5 for cid in scores}


def test_unfitted_scores_are_deterministic():
    """Same inputs must yield identical scores across calls and instances."""
    first = HybridScorer().score_content_for_user(user_id=1, candidate_ids=[10, 20, 30])
    second = HybridScorer().score_content_for_user(user_id=7, candidate_ids=[10, 20, 30])
    # Score depends only on content id, so it is stable regardless of user/instance.
    assert first == second


def test_returns_empty_dict_for_empty_candidates():
    scorer = HybridScorer()
    scores = scorer.score_content_for_user(user_id=1, candidate_ids=[])
    assert scores == {}


def test_observable_features_beat_repeated_negative_item():
    scorer = HybridScorer()
    useful = ContentItem(
        1, "PRODUTIVIDADE", 0.5, quality_score=0.9,
        topic_affinity=1.0, positive_events=3,
    )
    repeated = ContentItem(
        2, "ENTRETENIMENTO", 0.5, quality_score=0.5,
        negative_events=5, impression_count=25, age_hours=2000,
    )
    scores = scorer.score_items_for_user(7, [useful, repeated])
    assert scores[1] > scores[2]
    assert "matches_your_topics" in useful.explanations


def test_feedback_is_confidence_weighted_for_sparse_history():
    scorer = HybridScorer()
    sparse = ContentItem(
        10,
        "PRODUTIVIDADE",
        0.5,
        quality_score=0.6,
        positive_events=1,
        impression_count=1,
    )
    established = ContentItem(
        20,
        "PRODUTIVIDADE",
        0.5,
        quality_score=0.6,
        positive_events=20,
        impression_count=20,
    )

    scorer.score_items_for_user(7, [sparse, established])
    sparse_feedback, _, _ = _feedback_signal(1, 0, 1)
    established_feedback, _, _ = _feedback_signal(20, 0, 20)

    # Isolate calibration from the intentional novelty/repetition penalties in
    # the final rank: stronger evidence moves the posterior further from neutral.
    assert established_feedback > sparse_feedback
    assert "positive_history" in established.explanations
    assert "positive_history" not in sparse.explanations


def test_unreacted_impressions_are_a_weak_repetition_signal():
    scorer = HybridScorer()
    fresh = ContentItem(1, "PRODUTIVIDADE", 0.5, quality_score=0.7)
    repeatedly_skipped = ContentItem(
        2,
        "PRODUTIVIDADE",
        0.5,
        quality_score=0.7,
        impression_count=25,
    )

    scores = scorer.score_items_for_user(11, [fresh, repeatedly_skipped])

    assert scores[1] > scores[2]
    assert "repetition_penalty" in repeatedly_skipped.explanations


def test_observable_features_are_clamped_to_valid_ranges():
    scorer = HybridScorer()
    malformed = ContentItem(
        99,
        "PRODUTIVIDADE",
        0.5,
        quality_score=4.0,
        topic_affinity=-3.0,
        age_hours=-10.0,
        positive_events=-2,
        negative_events=-4,
        impression_count=-8,
    )

    score = scorer.score_items_for_user(1, [malformed])[99]

    assert 0.0 <= score <= 1.0


def test_quality_and_intent_beat_engagement_history():
    scorer = HybridScorer()
    aligned_quality = ContentItem(
        101, "PRODUTIVIDADE", 0.5,
        quality_score=0.9, topic_affinity=1.0,
    )
    engaging_but_weak = ContentItem(
        202, "ENTRETENIMENTO", 0.5,
        quality_score=0.3, topic_affinity=0.0,
        positive_events=30, impression_count=30,
    )

    scores = scorer.score_items_for_user(1, [aligned_quality, engaging_but_weak])

    assert scores[101] > scores[202]
    assert aligned_quality.attention_support > engaging_but_weak.attention_support
