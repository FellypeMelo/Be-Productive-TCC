import pytest
from src.infrastructure.hybrid_scorer import HybridScorer


def test_returns_fallback_scores_when_unfitted():
    scorer = HybridScorer()
    scores = scorer.score_content_for_user(user_id=1, candidate_ids=[10, 20, 30])

    assert scores == {10: 0.5, 20: 0.5, 30: 0.5}


def test_returns_empty_dict_for_empty_candidates():
    scorer = HybridScorer()
    scores = scorer.score_content_for_user(user_id=1, candidate_ids=[])
    assert scores == {}
