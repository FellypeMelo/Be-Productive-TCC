import pytest
from src.inference.hawkes_classifier import HawkesClassifier
from src.inference.safety_classifier import SafetyClassifierStub

def test_hawkes_classifier_logic():
    """Valida se o classificador distingue eventos rápidos (S1) de lentos (S2)."""
    classifier = HawkesClassifier()
    
    # Eventos rápidos (delay < 2s) -> Sistema 1 dominante
    events_s1 = [0.1, 0.5, 1.2]
    result_s1 = classifier.classify(events_s1)
    assert result_s1["system"] == 1
    assert result_s1["ratio"] > 1.0
    
    # Eventos lentos (delay > 10s) -> Sistema 2 dominante
    events_s2 = [15.0, 45.0, 120.0]
    result_s2 = classifier.classify(events_s2)
    assert result_s2["system"] == 2
    assert result_s2["ratio"] < 1.0

def test_safety_classifier_interface():
    """Garante que o stub de segurança segue o contrato min-norm."""
    classifier = SafetyClassifierStub()
    # Post aleatório
    prob = classifier.infer_probability({"text": "neutral content"})
    assert 0.0 <= prob <= 1.0
