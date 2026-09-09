from src.evaluation.experiment_metrics import intent_to_treat_report, sample_ratio_mismatch


def test_balanced_allocation_passes_srm():
    result = sample_ratio_mismatch(500, 500)
    assert result["mismatch"] is False
    assert result["treatment_share"] == 0.5


def test_intent_to_treat_report_uses_aggregate_metric():
    result = intent_to_treat_report([
        {"variant": "control", "primary_metric": 0.4},
        {"variant": "control", "primary_metric": 0.6},
        {"variant": "treatment", "primary_metric": 0.8},
        {"variant": "treatment", "primary_metric": 0.9},
    ])
    assert result["analysis"] == "intent_to_treat"
    assert result["difference_treatment_minus_control"] > 0
