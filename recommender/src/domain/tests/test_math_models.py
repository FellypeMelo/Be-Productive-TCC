import pytest
from src.domain.value_objects import QualityScore, AttentionReserve, SafetyProbability
from src.domain.math_models import calculate_quality_score, calculate_ego_depletion, calculate_hawkes_activation

def test_quality_score_min_aggregation():
    """
    Testa a Equação 3: O Penalty deve ser o min_m(1 - P_m(i)).
    Se há probabilidades de risco [0.8, 0.2, 0.1]:
    Fatores de penalidade = [1-0.8, 1-0.2, 1-0.1] = [0.2, 0.8, 0.9]
    O fator multiplicativo aplicado deve ser o mínimo (0.2).
    Se o base_score for 0.5, o QualityScore final deve ser 0.5 * 0.2 = 0.1
    """
    base_score = 0.5
    safety_probs = [
        SafetyProbability(0.8), # Alto risco
        SafetyProbability(0.2), # Baixo risco
        SafetyProbability(0.1)  # Muito baixo risco
    ]
    
    final_score = calculate_quality_score(base_score, safety_probs)
    
    # Assert return object is exactly a QualityScore
    assert isinstance(final_score, QualityScore)
    # 0.5 * min(1-0.8, 1-0.2, 1-0.1) = 0.5 * 0.2 = 0.10000000000000009 (float precision)
    assert pytest.approx(final_score.value, 0.001) == 0.1

def test_quality_score_no_penalty():
    """Sem flags (lista vazia), o penalty min_aggregation é 1.0."""
    base_score = 0.75
    final_score = calculate_quality_score(base_score, [])
    assert final_score.value == 0.75

def test_ego_depletion_edo():
    """
    Testa a cinética de Esgotamento do Ego (Eq 4 / Algoritmo 3).
    L(X, t) = k1 * v_scroll + k2 * v_alt
    Atualização: R = R - L * delta_t
    """
    initial_reserve = AttentionReserve(current=100.0, r_max=100.0)
    v_scroll = 50.0
    v_alt = 2.0
    k1 = 0.1
    k2 = 1.0
    delta_t = 1.0 # 1 segundo
    
    # L(X,t) = (0.1 * 50.0) + (1.0 * 2.0) = 5.0 + 2.0 = 7.0
    # R_new = 100.0 - (7.0 * 1.0) = 93.0
    
    new_reserve = calculate_ego_depletion(initial_reserve, v_scroll, v_alt, k1, k2, delta_t)
    
    assert isinstance(new_reserve, AttentionReserve)
    assert new_reserve.current == 93.0
    assert new_reserve.r_max == 100.0

def test_ego_depletion_saturates_at_zero():
    """Ego Reserve cannot drop below 0."""
    initial_reserve = AttentionReserve(current=5.0, r_max=100.0)
    # Depletion creates a reduction of 10.0
    v_scroll = 100.0
    v_alt = 0.0
    k1 = 0.1
    k2 = 1.0
    delta_t = 1.0
    
    new_reserve = calculate_ego_depletion(initial_reserve, v_scroll, v_alt, k1, k2, delta_t)
    assert new_reserve.current == 0.0
    
def test_system_2_activation_hawkes():
    """
    Testes de Hawkes (Equação 2) onde Sistema 2 retém o engajamento através de constantes beta baixas.
    """
    # alpha_2 = 0.5, beta_2 = 0.01 (decai 1% por T)
    time_delta = 10.0 # Segundos
    activation = calculate_hawkes_activation(alpha=0.5, beta=0.01, time_delta=time_delta)
    
    # 0.5 * e^(-0.01 * 10) = 0.5 * e^(-0.1) = ~0.452
    assert pytest.approx(activation, 0.01) == 0.452
