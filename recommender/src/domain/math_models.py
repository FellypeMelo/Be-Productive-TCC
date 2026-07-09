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
    """Contribuição de UM evento passado ao kernel de Hawkes: alpha*exp(-beta*dt).

    Primitivo de baixo nível (a excitação decorrente de um único evento a `time_delta`
    unidades no passado). A intensidade completa (Eq. 2) soma isto sobre o histórico —
    ver `hawkes_intensity`.
    """
    return alpha * math.exp(-beta * time_delta)


def hawkes_intensity(
    t: float,
    events_s1: List[float],
    events_s2: List[float],
    mu: float,
    alpha1: float,
    beta1: float,
    alpha2: float,
    beta2: float,
) -> dict:
    """Intensidade instantânea do processo de Hawkes bi-kernel (Eq. 2 do artigo).

        λ(t) = μ + Σ_{t_k∈𝒦, t_k<t} α₁·e^{−β₁(t−t_k)}
                 + Σ_{t_m∈ℳ, t_m<t} α₂·e^{−β₂(t−t_m)}

    - 𝒦 (events_s1): eventos de consumo rápido/impulsivo (Sistema 1) — salto forte (α₁),
      decaimento rápido (β₁ grande).
    - ℳ (events_s2): engajamento profundo/intencional (Sistema 2) — salto moderado (α₂),
      traço persistente (β₂ → 0).

    Retorna a intensidade total, as duas parcelas e a razão λ_s1/λ_s2 (>1 ⇒ estado
    dominado pelo Sistema 1, sinal de excitação residual / risco de doom-scroll).
    """
    lambda_s1 = sum(
        alpha1 * math.exp(-beta1 * (t - tk)) for tk in events_s1 if tk < t
    )
    lambda_s2 = sum(
        alpha2 * math.exp(-beta2 * (t - tm)) for tm in events_s2 if tm < t
    )
    total = mu + lambda_s1 + lambda_s2
    ratio = lambda_s1 / lambda_s2 if lambda_s2 > 1e-12 else float("inf") if lambda_s1 > 0 else 0.0
    return {
        "lambda_total": total,
        "lambda_s1": lambda_s1,
        "lambda_s2": lambda_s2,
        "ratio": ratio,
    }


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


def calculate_hyperbolic_discount(value: float, k: float, delay: float) -> float:
    """
    Equation 5: Hyperbolic Discounting.
    V_p = V / (1 + k * D)

    Args:
        value: Intrinsic value of the reward (V)
        k: Impulsivity constant (discount rate)
        delay: Time delay until reward (D)

    Returns:
        Perceived value V_p at decision time
    """
    if value < 0:
        raise ValueError("value must be non-negative")
    if k < 0:
        raise ValueError("k (impulsivity) must be non-negative")
    if delay < 0:
        raise ValueError("delay must be non-negative")
    return value / (1.0 + k * delay)
