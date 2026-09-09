import numpy as np

# np.trapz foi renomeado para np.trapezoid no NumPy 2.0; mantém compatibilidade.
_trapezoid = getattr(np, "trapezoid", None) or getattr(np, "trapz")


def calculate_auc(r_curve: list, dt: float) -> float:
    """Integral sob a curva de Ego Depletion (Regra do Trapézio)."""
    return _trapezoid(r_curve, dx=dt)

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
