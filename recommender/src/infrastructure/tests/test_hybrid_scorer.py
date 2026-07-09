import pytest
from src.infrastructure.hybrid_scorer import HybridScorer


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
