import pytest

from src.evaluation.ab_report import build_report


def test_report_rejects_raw_telemetry():
    with pytest.raises(ValueError, match="raw telemetry"):
        build_report({"experiment_id": "sustainable-attention-v1", "rows": [{"variant": "control", "primary_metric": 0.5, "v_scroll": 2}]})
