"""Pre-flight and analysis gate for sustainable-attention-v1.

The contract mode is safe for CI and uses a tiny synthetic fixture. Analysis
mode is for participant-level aggregates and enforces the pre-registered sample
and guardrail rules. Neither mode accepts raw behavioral telemetry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.evaluation.ab_report import _contains_forbidden
from src.evaluation.experiment_metrics import intent_to_treat_report

EXPERIMENT_ID = "sustainable-attention-v1"
ASSIGNMENT_VERSION = "sha256-v1"


def _validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    if manifest.get("experiment_id") != EXPERIMENT_ID:
        errors.append("manifest experiment_id mismatch")
    if manifest.get("assignment_version") != ASSIGNMENT_VERSION:
        errors.append("manifest assignment_version mismatch")
    allocation = manifest.get("allocation", {})
    if allocation.get("control") != 0.5 or allocation.get("treatment") != 0.5:
        errors.append("allocation must be 50/50")
    if manifest.get("primary_metric") != "normalized_reserve_auc_7d":
        errors.append("primary metric must remain normalized_reserve_auc_7d")
    if manifest.get("analysis", {}).get("method") != "intent_to_treat":
        errors.append("analysis method must remain intent_to_treat")
    return errors


def _validate_rows(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: dict[object, str] = {}
    for row in rows:
        user_id = row.get("user_id")
        variant = row.get("variant")
        if not isinstance(user_id, int) or user_id < 1:
            errors.append("user_id must be a positive integer")
            continue
        if user_id in seen:
            if seen[user_id] != variant:
                errors.append(f"user {user_id} appears in both arms")
            else:
                errors.append(f"user {user_id} appears more than once")
        seen[user_id] = variant
    return errors


def _validate_guardrails(payload: dict, manifest: dict) -> list[str]:
    errors: list[str] = []
    values = payload.get("guardrails", {})
    limits = manifest.get("guardrails", {})
    for metric, limit in limits.items():
        if metric == "srm_alpha":
            continue
        observed = values.get(metric.removesuffix("_delta"))
        if not isinstance(observed, dict) or not all(arm in observed for arm in ("control", "treatment")):
            continue
        try:
            delta = float(observed["treatment"]) - float(observed["control"])
            threshold = float(limit)
        except (TypeError, ValueError):
            errors.append(f"guardrail {metric} must contain finite numbers")
            continue
        if metric.endswith("retention_7d_delta"):
            if delta < threshold:
                errors.append(f"guardrail {metric} below limit: {delta}")
        elif delta > threshold:
            errors.append(f"guardrail {metric} above limit: {delta}")
    return errors


def run_gate(manifest: dict, payload: dict, mode: str = "contract") -> dict:
    errors = _validate_manifest(manifest)
    if payload.get("experiment_id") != EXPERIMENT_ID:
        errors.append("fixture experiment_id mismatch")
    if payload.get("assignment_version") != ASSIGNMENT_VERSION:
        errors.append("fixture assignment_version mismatch")
    if _contains_forbidden(payload):
        errors.append("raw telemetry is not accepted")
    rows = payload.get("rows", [])
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty list")
        rows = []
    errors.extend(_validate_rows(rows))
    try:
        report = intent_to_treat_report(rows)
    except (TypeError, ValueError) as exc:
        errors.append(str(exc))
        report = {}
    if report.get("srm", {}).get("mismatch"):
        errors.append("sample ratio mismatch detected")
    if mode == "analysis":
        minimum = manifest["analysis"]["minimum_exposure_per_arm"]
        for arm, count in report.get("arms", {}).items():
            if count < minimum:
                errors.append(f"{arm} has {count} exposures; minimum is {minimum}")
        errors.extend(_validate_guardrails(payload, manifest))
    return {"passed": not errors, "mode": mode, "errors": errors, "report": report}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--mode", choices=("contract", "analysis"), default="contract")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_gate(manifest, payload, args.mode)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["passed"] else 1
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ab-gate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
