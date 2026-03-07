import numpy as np

def calculate_auc(r_curve: list, dt: float) -> float:
    """Implementa cálculo de Integral sob a curva de Ego Depletion com a Regra do Trapézio"""
    return np.trapz(r_curve, dx=dt)

def calculate_kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """
    Calcula a Divergência KL entre Intenção (P) e Alocação Real (Q).
    Usa epsilon (pequena compensação) para evitar divisões por zero ou log(0).
    """
    epsilon = 1e-10
    p_safe = p + epsilon
    q_safe = q + epsilon
    
    # Normaliza
    p_safe = p_safe / np.sum(p_safe)
    q_safe = q_safe / np.sum(q_safe)
    
    return np.sum(p_safe * np.log(p_safe / q_safe))
