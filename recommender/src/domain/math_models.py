import math
import random
from typing import List
from src.domain.value_objects import QualityScore, AttentionReserve, SafetyProbability

def calculate_quality_score(
    base_score: float, 
    safety_probs: List[SafetyProbability]
) -> QualityScore:
    """Implementa a Equação 3 com Min-Aggregation Penalty."""
    if not safety_probs:
        return QualityScore(base_score)
        
    min_penalty_factor = min(1.0 - p.value for p in safety_probs)
    final_score = base_score * min_penalty_factor
    return QualityScore(max(0.0, min(1.0, final_score)))

def calculate_ego_depletion(
    reserve: AttentionReserve,
    v_scroll: float,
    v_alt: float,
    k1: float,
    k2: float,
    delta_t: float,
    mu_rest: float = 0.0
) -> AttentionReserve:
    """Implementa a cinética de Esgotamento do Ego (Eq 4).
    dR/dt = μ_rest·(R_max - R(t)) - (κ₁·v_scroll + κ₂·v_alt)
    """
    l_atual = (k1 * v_scroll) + (k2 * v_alt)
    recovery = mu_rest * (reserve.r_max - reserve.current)
    delta = (recovery - l_atual) * delta_t

    new_current = max(0.0, min(reserve.r_max, reserve.current + delta))
    return AttentionReserve(current=new_current, r_max=reserve.r_max)


def calculate_hawkes_activation(alpha: float, beta: float, time_delta: float) -> float:
    """Implementa a variação do processo auto-excitante de Hawkes (Eq 2)."""
    return alpha * math.exp(-beta * time_delta)


def thompson_sampling_choice(
    alpha_s1: float, beta_s1: float,
    alpha_s2: float, beta_s2: float
) -> int:
    """Thompson Sampling com 2 braços via distribuição Beta.
    Retorna 0 (S1/impulsivo) ou 1 (S2/deliberado).
    """
    theta_s1 = random.betavariate(alpha_s1, beta_s1)
    theta_s2 = random.betavariate(alpha_s2, beta_s2)
    return 0 if theta_s1 >= theta_s2 else 1


def calculate_kl_divergence(
    p: List[float], q: List[float], epsilon: float = 1e-12
) -> float:
    """D_KL(P || Q) = Σᵢ P(i)·log(P(i) / Q(i)).
    Suaviza com epsilon para evitar log(0).
    """
    kl = 0.0
    for pi, qi in zip(p, q):
        pi_s = max(pi, epsilon)
        qi_s = max(qi, epsilon)
        kl += pi_s * math.log(pi_s / qi_s)
    return kl
