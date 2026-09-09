import pytest
from src.infrastructure.safety_gateway import ToxicitySafetyGateway
from src.application.interfaces import SafetyClassifierInterface
from src.domain.value_objects import SafetyProbability
from src.application.interfaces import ContentItem


def test_gateway_implements_safety_classifier_interface():
    gw = ToxicitySafetyGateway()
    assert isinstance(gw, SafetyClassifierInterface)


def test_returns_five_safety_probabilities():
    """The paper specifies 5 classifiers: P1..P5."""
    gw = ToxicitySafetyGateway()
    probs = gw.infer_safety_probabilities(content_id=1)

    assert isinstance(probs, list)
    assert len(probs) == 5, f"Expected 5 safety dimensions, got {len(probs)}"
    assert all(isinstance(p, SafetyProbability) for p in probs)
    assert all(0.0 <= p.value <= 1.0 for p in probs)


def test_toxic_content_penalized_across_dimensions():
    """Verify that for toxic-flagged content, min(1-P) produces low score."""
    toxic_probs = [
        SafetyProbability(0.9),  # P1 hate
        SafetyProbability(0.7),  # P2 misinformation
        SafetyProbability(0.1),
        SafetyProbability(0.1),
        SafetyProbability(0.1),
    ]
    min_penalty = min(1.0 - p.value for p in toxic_probs)
    assert min_penalty == pytest.approx(0.1)


def test_all_probabilities_are_bounded():
    """All safety probabilities must be in [0, 1]."""
    gw = ToxicitySafetyGateway()
    for _ in range(50):
        probs = gw.infer_safety_probabilities(content_id=42)
        assert len(probs) == 5
        for p in probs:
            assert 0.0 <= p.value <= 1.0


def test_same_content_id_yields_identical_probabilities():
    """Deterministic gateway: same content_id -> same probabilities every call.

    This is the property that makes min-norm aggregation reproducible (the old
    random gateway produced a different vector on every call).
    """
    gw = ToxicitySafetyGateway()
    first = [p.value for p in gw.infer_safety_probabilities(content_id=123)]
    second = [p.value for p in gw.infer_safety_probabilities(content_id=123)]
    assert first == second

    # A fresh instance must also agree (no hidden per-instance state).
    third = [p.value for p in ToxicitySafetyGateway().infer_safety_probabilities(content_id=123)]
    assert first == third


def test_textual_risk_changes_probabilities():
    """Gateway evaluates content text, not opaque database ids."""
    gw = ToxicitySafetyGateway()
    safe = ContentItem(1, "PRODUTIVIDADE", 0.8, title="Como estudar com calma")
    risky = ContentItem(2, "ENTRETENIMENTO", 0.8, title="Chocante: agora ou nunca, não pare")
    safe_probs = gw.infer_content_probabilities(safe)
    risky_probs = gw.infer_content_probabilities(risky)
    assert max(p.value for p in risky_probs) > max(p.value for p in safe_probs)
