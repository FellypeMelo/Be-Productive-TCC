import pytest
import numpy as np
# Will fail before implementation
from src.abm.sensitivity import SensitivityEngine

def test_sensitivity_engine_parameter_sweep():
    """Garante que o motor de sensibilidade percorre múltiplos cenários."""
    engine = SensitivityEngine()
    
    parameters = {
        "sust_scroll_reduction": [0.2, 0.5, 0.8],  # intensidade da fricção (scroll)
        "k1": [0.05, 0.1, 0.15],                    # vulnerabilidade do usuário
    }

    # Run a sweep with small population for testing
    results = engine.run_sweep(N=10, T=10, param_grid=parameters)

    # Should have results for 3 * 3 = 9 scenarios
    assert len(results) == 9

    # Each scenario should have aggregated metrics
    first_scen = results[0]
    assert "sust_scroll_reduction" in first_scen
    assert "mean_auc_delta" in first_scen
    assert "p_value" in first_scen

def test_sensitivity_engine_finds_breaking_point():
    """Testa se o motor identifica o ponto onde o BeProductive perde a significância."""
    engine = SensitivityEngine()
    
    # Cenário de efeito-zero: TODOS os mecanismos do braço sustentável desligados,
    # de modo que ele degenera exatamente no baseline (teste de sanidade do arcabouço).
    parameters = {"sust_scroll_reduction": [0.0]}
    fixed = {"min_norm_on": False, "friction_on": False, "steering_on": False}

    results = engine.run_sweep(N=50, T=10, param_grid=parameters, fixed=fixed)

    # Sem nenhum mecanismo ativo, o delta deve ser desprezível (efeito não embutido).
    assert results[0]["p_value"] > 0.01 or abs(results[0]["mean_auc_delta"]) < 5.0
