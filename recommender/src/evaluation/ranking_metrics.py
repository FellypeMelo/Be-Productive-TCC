import math
from collections.abc import Iterable, Sequence


def precision_at_k(ranked: Sequence[int], relevant: set[int], k: int) -> float:
    selected = ranked[:k]
    return sum(item in relevant for item in selected) / k if k > 0 else 0.0


def recall_at_k(ranked: Sequence[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(item in relevant for item in ranked[:k]) / len(relevant)


def ndcg_at_k(ranked: Sequence[int], relevance: dict[int, float], k: int) -> float:
    gains = [relevance.get(item, 0.0) for item in ranked[:k]]
    dcg = sum((2**gain - 1) / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = sum((2**gain - 1) / math.log2(index + 2) for index, gain in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def catalog_coverage(rankings: Iterable[Sequence[int]], catalog: set[int]) -> float:
    if not catalog:
        return 0.0
    recommended = {item for ranking in rankings for item in ranking}
    return len(recommended & catalog) / len(catalog)


def category_diversity(ranked: Sequence[int], categories: dict[int, str], k: int) -> float:
    selected = ranked[:k]
    if len(selected) < 2:
        return 0.0
    pairs = len(selected) * (len(selected) - 1) / 2
    different = sum(
        categories.get(selected[i]) != categories.get(selected[j])
        for i in range(len(selected)) for j in range(i + 1, len(selected))
    )
    return different / pairs
