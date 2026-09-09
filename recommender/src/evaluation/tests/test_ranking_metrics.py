import pytest

from src.evaluation.ranking_metrics import (
    catalog_coverage,
    category_diversity,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def test_ranking_metrics_known_example():
    ranked = [1, 3, 2]
    relevant = {1, 2}
    assert precision_at_k(ranked, relevant, 2) == 0.5
    assert recall_at_k(ranked, relevant, 3) == 1.0
    assert ndcg_at_k(ranked, {1: 2.0, 2: 1.0}, 3) == pytest.approx(0.96394, abs=1e-4)


def test_coverage_and_diversity():
    assert catalog_coverage([[1, 2], [2, 3]], {1, 2, 3, 4}) == 0.75
    assert category_diversity([1, 2, 3], {1: "A", 2: "B", 3: "A"}, 3) == pytest.approx(2 / 3)
