import pytest
import numpy as np
# Will fail before implementation
from src.abm.sensitivity import SensitivityEngine

def test_sensitivity_engine_parameter_sweep():
    """Garante que o motor de sensibilidade percorre múltiplos cenários."""
    engine = SensitivityEngine()
    
    parameters = {
        "v_scroll_reduction": [0.1, 0.5, 0.9], # 10%, 50%, 90% reduction
        "kappa_variation": [0.5, 1.0, 1.5]
    }
    
    # Run a sweep with small population for testing
    results = engine.run_sweep(N=10, T=10, param_grid=parameters)
    
    # Should have results for 3 * 3 = 9 scenarios
    assert len(results) == 9
    
    # Each scenario should have aggregated metrics
    first_scen = results[0]
    assert "v_scroll_reduction" in first_scen
    assert "mean_auc_delta" in first_scen
    assert "p_value" in first_scen

def test_sensitivity_engine_finds_breaking_point():
    """Testa se o motor identifica o ponto onde o BeProductive perde a significância."""
    engine = SensitivityEngine()
    
    # Testing with zero effect scenario
    parameters = {
        "v_scroll_reduction": [0.0], # Zero reduction
        "kappa_variation": [1.0]
    }
    
    results = engine.run_sweep(N=20, T=10, param_grid=parameters)
    
    # In zero effect, p_value should be high or delta near zero
    assert results[0]["p_value"] > 0.05 or abs(results[0]["mean_auc_delta"]) < 1.0
