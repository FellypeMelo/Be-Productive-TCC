"""Offline, privacy-safe checks for the real-user experiment contract."""

from __future__ import annotations

import math
from statistics import fmean, stdev
from typing import Iterable


def _chi_square_p_value(statistic: float) -> float:
    return math.erfc(math.sqrt(max(0.0, statistic) / 2.0))


def sample_ratio_mismatch(control_count: int, treatment_count: int, expected_treatment_share: float = 0.5, alpha: float = 0.001) -> dict[str, float | bool]:
    """Check whether observed allocation differs from the manifest ratio."""
    if control_count < 0 or treatment_count < 0:
        raise ValueError("arm counts cannot be negative")
    if not 0 < expected_treatment_share < 1:
        raise ValueError("expected share must be between zero and one")
    total = control_count + treatment_count
    if total == 0:
        return {"p_value": 0.0, "mismatch": True, "treatment_share": 0.0}
    expected_control = total * (1.0 - expected_treatment_share)
    expected_treatment = total * expected_treatment_share
    statistic = ((control_count - expected_control) ** 2 / expected_control) + ((treatment_count - expected_treatment) ** 2 / expected_treatment)
    p_value = _chi_square_p_value(statistic)
    return {"p_value": p_value, "mismatch": p_value < alpha, "treatment_share": treatment_count / total}


def _mean_ci(values: list[float], confidence_z: float = 1.96) -> tuple[float, float]:
    if not values:
        raise ValueError("at least one metric value is required")
    if len(values) == 1:
        return fmean(values), 0.0
    return fmean(values), confidence_z * stdev(values) / math.sqrt(len(values))


def intent_to_treat_report(rows: Iterable[dict]) -> dict:
    """Summarize assigned users using participant-level aggregates only."""
    grouped: dict[str, list[float]] = {"control": [], "treatment": []}
    for row in rows:
        variant = row.get("variant")
        if variant not in grouped:
            raise ValueError("rows must use control or treatment")
        value = row.get("primary_metric")
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("primary_metric must be a finite number")
        grouped[variant].append(float(value))

    control, treatment = grouped["control"], grouped["treatment"]
    srm = sample_ratio_mismatch(len(control), len(treatment))
    result: dict = {"arms": {"control": len(control), "treatment": len(treatment)}, "srm": srm, "analysis": "intent_to_treat"}
    if not control or not treatment:
        return result
    control_mean, control_margin = _mean_ci(control)
    treatment_mean, treatment_margin = _mean_ci(treatment)
    difference = treatment_mean - control_mean
    standard_error = math.sqrt((stdev(control) ** 2 / len(control) if len(control) > 1 else 0.0) + (stdev(treatment) ** 2 / len(treatment) if len(treatment) > 1 else 0.0))
    result.update({
        "means": {"control": control_mean, "treatment": treatment_mean},
        "difference_treatment_minus_control": difference,
        "difference_ci95": [difference - 1.96 * standard_error, difference + 1.96 * standard_error],
        "arm_ci95_half_width": {"control": control_margin, "treatment": treatment_margin},
    })
    return result
