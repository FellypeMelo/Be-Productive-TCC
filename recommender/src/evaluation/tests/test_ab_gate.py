import json
from pathlib import Path

from src.evaluation.ab_gate import run_gate


ROOT = Path(__file__).parents[3]


def test_contract_fixture_passes():
    manifest = json.loads((ROOT / "experiment_manifest.sustainable-attention-v1.json").read_text())
    fixture = json.loads((ROOT / "evaluation_gate_fixture.json").read_text())
    result = run_gate(manifest, fixture)
    assert result["passed"] is True


def test_analysis_mode_requires_planned_sample():
    manifest = json.loads((ROOT / "experiment_manifest.sustainable-attention-v1.json").read_text())
    fixture = json.loads((ROOT / "evaluation_gate_fixture.json").read_text())
    result = run_gate(manifest, fixture, mode="analysis")
    assert result["passed"] is False
    assert any("minimum" in error for error in result["errors"])


def test_analysis_mode_rejects_guardrail_regression():
    manifest = json.loads((ROOT / "experiment_manifest.sustainable-attention-v1.json").read_text())
    fixture = json.loads((ROOT / "evaluation_gate_fixture.json").read_text())
    fixture["guardrails"]["retention_7d"]["treatment"] = 0.70
    result = run_gate(manifest, fixture, mode="analysis")
    assert any("retention_7d_delta" in error for error in result["errors"])
