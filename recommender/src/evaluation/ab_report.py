"""CLI for the pre-registered, aggregate-only experiment report.

Usage inside the recommender container:
    python -m src.evaluation.ab_report input.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.evaluation.experiment_metrics import intent_to_treat_report

_FORBIDDEN_KEYS = {"v_scroll", "v_alt", "reserve", "friction", "raw_telemetry", "navigation_history"}


def _contains_forbidden(value: object) -> bool:
    if isinstance(value, dict):
        if _FORBIDDEN_KEYS.intersection(value):
            return True
        return any(_contains_forbidden(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden(child) for child in value)
    return False


def build_report(payload: dict) -> dict:
    if payload.get("experiment_id") != "sustainable-attention-v1":
        raise ValueError("unexpected experiment_id")
    if _contains_forbidden(payload):
        raise ValueError("raw telemetry is not accepted by the experiment report")
    return intent_to_treat_report(payload.get("rows", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an aggregate-only ITT report")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(build_report(payload), ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ab-report: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
