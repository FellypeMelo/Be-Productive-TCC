import pytest
import numpy as np
# Will fail before green phase
from src.abm.metrics import calculate_auc, calculate_kl_divergence

def test_auc_calculation():
    """Testa o cálculo da integral de área (AUC) da saturação atencional."""
    # R(t) curve: linear drop from 100 over 5 timesteps 
    # [100, 80, 60, 40, 20, 0]
    r_curve = [100, 80, 60, 40, 20, 0]
    dt = 1.0 # time delta is 1
    # AUC geometry (trapezoidal rule): 
    # (100+80)/2 + (80+60)/2 + (60+40)/2 + (40+20)/2 + (20+0)/2
    # = 90 + 70 + 50 + 30 + 10 = 250
    auc = calculate_auc(r_curve, dt)
    assert pytest.approx(auc, 0.1) == 250.0

def test_kl_divergence():
    """Testa a Divergência de Kullback-Leibler entre intenção vs. alocação."""
    # P: Intended Distribution [0.8 productivity, 0.2 entertainment]
    # Q: Actual Consumption   [0.5 productivity, 0.5 entertainment]
    
    p = np.array([0.8, 0.2])
    q = np.array([0.5, 0.5])
    
    kl = calculate_kl_divergence(p, q)
    
    # Expected: 0.8 * ln(0.8/0.5) + 0.2 * ln(0.2/0.5) = 0.8*0.470003 + 0.2*(-0.91629) = 0.3760 - 0.1832 = 0.1927
    assert pytest.approx(kl, 0.01) == 0.1927
    
def test_kl_divergence_identical():
    """If intention perfectly matches consumption, KL div must be 0."""
    p = np.array([0.7, 0.3])
    q = np.array([0.7, 0.3])
    kl = calculate_kl_divergence(p, q)
    assert pytest.approx(kl, 0.001) == 0.0
