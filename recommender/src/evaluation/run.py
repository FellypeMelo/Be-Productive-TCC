import argparse
import json
from pathlib import Path

from src.evaluation.ranking_metrics import (
    catalog_coverage,
    category_diversity,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def evaluate(payload: dict, k: int) -> dict:
    sessions = payload["sessions"]
    rankings = [session["ranked"] for session in sessions]
    precision = []
    recall = []
    ndcg = []
    diversity = []
    categories = {int(key): value for key, value in payload["categories"].items()}
    for session in sessions:
        ranked = session["ranked"]
        relevance = {int(key): value for key, value in session["relevance"].items()}
        relevant = {item for item, value in relevance.items() if value > 0}
        precision.append(precision_at_k(ranked, relevant, k))
        recall.append(recall_at_k(ranked, relevant, k))
        ndcg.append(ndcg_at_k(ranked, relevance, k))
        diversity.append(category_diversity(ranked, categories, k))
    mean = lambda values: sum(values) / len(values) if values else 0.0
    return {
        "k": k,
        "sessions": len(sessions),
        "precision_at_k": mean(precision),
        "recall_at_k": mean(recall),
        "ndcg_at_k": mean(ndcg),
        "category_diversity": mean(diversity),
        "catalog_coverage": catalog_coverage(rankings, set(payload["catalog"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate an offline ranking fixture")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()
    result = evaluate(json.loads(args.input.read_text(encoding="utf-8")), args.k)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
