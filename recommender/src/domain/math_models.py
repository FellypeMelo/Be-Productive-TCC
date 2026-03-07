import math
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
    delta_t: float
) -> AttentionReserve:
    """Implementa a cinética de Esgotamento do Ego (Eq 4)."""
    l_atual = (k1 * v_scroll) + (k2 * v_alt)
    depletion = l_atual * delta_t
    
    new_current = max(0.0, min(reserve.r_max, reserve.current - depletion))
    return AttentionReserve(current=new_current, r_max=reserve.r_max)

def calculate_hawkes_activation(alpha: float, beta: float, time_delta: float) -> float:
    """Implementa a variação do processo auto-excitante de Hawkes (Eq 2)."""
    return alpha * math.exp(-beta * time_delta)
