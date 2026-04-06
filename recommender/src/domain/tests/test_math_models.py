import pytest
from src.domain.value_objects import QualityScore, AttentionReserve, SafetyProbability
from src.domain.math_models import calculate_quality_score, calculate_ego_depletion, calculate_hawkes_activation, calculate_hyperbolic_discount

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

def test_ego_depletion_with_recovery():
    """
    FASE RED — Eq. 4 completa: dR/dt = μ_rest·(R_max - R) - L(X,t)
    Cenário de recuperação pura (L = 0):
    recovery = 0.1 * (100 - 50) = 5.0
    delta = (5.0 - 0.0) * 1.0 = 5.0
    new_current = 50 + 5.0 = 55.0
    """
    reserve = AttentionReserve(current=50.0, r_max=100.0)
    result = calculate_ego_depletion(
        reserve, v_scroll=0.0, v_alt=0.0,
        k1=0.1, k2=0.5, delta_t=1.0, mu_rest=0.1
    )
    assert isinstance(result, AttentionReserve)
    assert pytest.approx(result.current, abs=0.001) == 55.0

def test_ego_depletion_saturates_even_with_recovery():
    """
    FASE RED — Verifica saturação em zero quando L >> recovery.
    L = (0.1 * 1000) + (1.0 * 0) = 100.0
    recovery = 0.1 * (100 - 5) = 9.5
    delta = (9.5 - 100.0) * 1.0 = -90.5
    new_current = max(0, 5 + (-90.5)) = 0.0
    """
    reserve = AttentionReserve(current=5.0, r_max=100.0)
    result = calculate_ego_depletion(
        reserve, v_scroll=1000.0, v_alt=0.0,
        k1=0.1, k2=1.0, delta_t=1.0, mu_rest=0.1
    )
    assert result.current == 0.0

def test_thompson_sampling_choice_favors_dominant_arm():
    """
    FASE RED — Grupo 4: Thompson Sampling via distribuição Beta.
    Com priors fortes alpha_s1=100, beta_s1=1 (S1 dominante),
    a maioria das N amostras deve retornar 0 (S1).
    """
    from src.domain.math_models import thompson_sampling_choice

    choices = [thompson_sampling_choice(
        alpha_s1=100.0, beta_s1=1.0,
        alpha_s2=1.0, beta_s2=100.0
    ) for _ in range(100)]

    # Com priors tão polarizados, >90% devem ser S1 (idx 0)
    s1_count = sum(1 for c in choices if c == 0)
    assert s1_count > 90

def test_thompson_sampling_returns_valid_arm_index():
    """Retorno deve ser 0 ou 1."""
    from src.domain.math_models import thompson_sampling_choice

    for _ in range(50):
        arm = thompson_sampling_choice(
            alpha_s1=1.0, beta_s1=1.0,
            alpha_s2=1.0, beta_s2=1.0
        )
        assert arm in (0, 1)

def test_kl_divergence_zero_for_identical():
    """KL(P || Q) = 0 quando P == Q."""
    from src.domain.math_models import calculate_kl_divergence
    assert calculate_kl_divergence([0.5, 0.5], [0.5, 0.5]) == pytest.approx(0.0, abs=1e-10)

def test_kl_divergence_positive_for_different():
    """KL(P || Q) > 0 quando P ≠ Q."""
    from src.domain.math_models import calculate_kl_divergence
    result = calculate_kl_divergence([0.9, 0.1], [0.5, 0.5])
    assert result > 0

def test_kl_divergence_asymmetric():
    """KL(P||Q) ≠ KL(Q||P) — KL é assimétrica."""
    from src.domain.math_models import calculate_kl_divergence
    kl_pq = calculate_kl_divergence([0.9, 0.1], [0.5, 0.5])
    kl_qp = calculate_kl_divergence([0.5, 0.5], [0.9, 0.1])
    assert kl_pq != pytest.approx(kl_qp, abs=1e-8)


def test_hyperbolic_discount_immediate_reward():
    """When delay=0, perceived value equals intrinsic value."""
    assert calculate_hyperbolic_discount(100.0, 0.5, 0.0) == 100.0


def test_hyperbolic_discount_delayed_reward():
    """Delayed reward should have lower perceived value."""
    immediate = calculate_hyperbolic_discount(100.0, 0.5, 0.0)
    delayed = calculate_hyperbolic_discount(100.0, 0.5, 10.0)
    assert delayed < immediate
    assert delayed == pytest.approx(100.0 / (1 + 0.5 * 10))  # = 16.67


def test_hyperbolic_discount_high_impulsivity():
    """Higher k (impulsivity) means steeper discount."""
    low_k = calculate_hyperbolic_discount(100.0, 0.1, 5.0)
    high_k = calculate_hyperbolic_discount(100.0, 1.0, 5.0)
    assert high_k < low_k


def test_hyperbolic_discount_zero_value():
    """Zero value always returns zero."""
    assert calculate_hyperbolic_discount(0.0, 0.5, 10.0) == 0.0


def test_hyperbolic_discount_invalid_negative_value():
    """Negative value should raise ValueError."""
    with pytest.raises(ValueError, match="value must be non-negative"):
        calculate_hyperbolic_discount(-10.0, 0.5, 5.0)


def test_hyperbolic_discount_invalid_negative_delay():
    """Negative delay should raise ValueError."""
    with pytest.raises(ValueError, match="delay must be non-negative"):
        calculate_hyperbolic_discount(100.0, 0.5, -1.0)

