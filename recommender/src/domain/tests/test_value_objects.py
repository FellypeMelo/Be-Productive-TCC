import pytest
from src.domain.value_objects import QualityScore, AttentionReserve, SafetyProbability

def test_quality_score_valid_creation():
    """QualityScore must accept values between 0.0 and 1.0."""
    score = QualityScore(0.75)
    assert score.value == 0.75

def test_quality_score_invalid_creation():
    """QualityScore must raise ValueError for values outside [0, 1]."""
    with pytest.raises(ValueError):
        QualityScore(-0.1)
    
    with pytest.raises(ValueError):
        QualityScore(1.1)

def test_attention_reserve_valid_creation():
    """AttentionReserve must be initialized correctly within [0, R_max]."""
    reserve = AttentionReserve(current=50.0, r_max=100.0)
    assert reserve.current == 50.0
    assert reserve.r_max == 100.0

def test_attention_reserve_invalid_negative():
    """AttentionReserve must raise ValueError for negative values."""
    with pytest.raises(ValueError):
        AttentionReserve(current=-5.0, r_max=100.0)
        
def test_attention_reserve_invalid_exceeds_max():
    """AttentionReserve must raise ValueError if current > R_max."""
    with pytest.raises(ValueError):
        AttentionReserve(current=150.0, r_max=100.0)

def test_safety_probability_validation():
    """SafetyProbability must be between 0 and 1."""
    valid_prob = SafetyProbability(0.9)
    assert valid_prob.value == 0.9
    
    with pytest.raises(ValueError):
        SafetyProbability(1.01)
        
    with pytest.raises(ValueError):
        SafetyProbability(-0.01)
