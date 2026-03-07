import pytest
import numpy as np
# Will fail before implementation
from src.abm.stats import calculate_p_value, calculate_effect_size

def test_p_value_calculation():
    """Garante que o teste estatístico detecta diferenças significativas."""
    # Group A: High retention energy
    group_a = np.random.normal(loc=100, scale=5, size=100)
    # Group B: Decayed energy
    group_b = np.random.normal(loc=50, scale=10, size=100)
    
    p_val = calculate_p_value(group_a, group_b)
    
    # Distributions are clearly different, p-value should be near zero (< 0.01)
    assert p_val < 0.01

def test_p_value_identical_distributions():
    """Se as distribuições forem idênticas, o p-value deve ser alto."""
    data = np.random.normal(loc=100, scale=10, size=500)
    p_val = calculate_p_value(data, data)
    
    # Comparison of same data should yield p > 0.05
    assert p_val > 0.05

def test_cohens_d_effect_size():
    """Garante o cálculo do Cohen's d para a magnitude do benefício."""
    # Case with clear positive effect
    group_sust = np.array([10, 11, 12, 10, 11]) # mean 10.8
    group_base = np.array([5, 6, 5, 4, 5])      # mean 5.0
    
    d = calculate_effect_size(group_sust, group_base)
    
    # d should be large (> 0.8 is generally considered large)
    assert d > 1.0
