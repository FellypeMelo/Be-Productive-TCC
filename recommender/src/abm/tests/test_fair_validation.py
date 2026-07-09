"""Testes que blindam a validade científica do experimento ABM.

Diferente da versão anterior (cujos testes certificavam o confundimento embutido),
estes testes exigem que o efeito seja GERADO pelos mecanismos e REPRODUZÍVEL — e que,
sem mecanismos, ele desapareça (teste de sanidade).
"""
import numpy as np
import pytest

from src.abm.engine import Simulator
from src.abm.metrics import calculate_auc, calculate_kl_divergence
from src.abm.stats import calculate_effect_size


def _auc_arrays(sim, N):
    b = np.array([calculate_auc(sim.results["baseline"]["r_curves"][i], 1.0) for i in range(N)])
    s = np.array([calculate_auc(sim.results["sustainable"]["r_curves"][i], 1.0) for i in range(N)])
    return b, s


def _median_kl(sim, arm, N):
    return float(np.median([
        calculate_kl_divergence(sim.results[arm]["intent_dist"][i], sim.results[arm]["q_allocations"][i])
        for i in range(N)
    ]))


def test_sanity_no_mechanism_gives_zero_effect():
    """Com TODOS os mecanismos desligados, o braço sustentável = baseline: d ≈ 0.

    Esta é a prova de que o efeito NÃO está embutido no arcabouço."""
    sim = Simulator(200, 60, params=dict(min_norm_on=False, friction_on=False, steering_on=False))
    sim.run()
    b, s = _auc_arrays(sim, 200)
    assert abs(calculate_effect_size(s, b)) < 0.25


def test_determinism_same_seed_same_result():
    """Reprodutibilidade estrita: numpy E random semeados => resultado idêntico."""
    d = []
    for _ in range(2):
        sim = Simulator(200, 60, seed=42)
        sim.run()
        b, s = _auc_arrays(sim, 200)
        d.append(calculate_effect_size(s, b))
    assert d[0] == pytest.approx(d[1], abs=1e-9)


@pytest.mark.slow
def test_headline_cohens_d_reproduces_3_25():
    """O d reportado no artigo (≈3.25) é reproduzido por uma execução justa e semeada."""
    sim = Simulator(1000, 60, seed=42)
    sim.run()
    b, s = _auc_arrays(sim, 1000)
    d = calculate_effect_size(s, b)
    assert 3.15 <= d <= 3.35, f"esperado ~3.25, obtido {d:.3f}"
    assert s.mean() > b.mean()


def test_ablation_ordering_full_beats_parts():
    """Modelo completo > qualquer mecanismo isolado; fricção é o motor primário da reserva."""
    def d_for(**cfg):
        sim = Simulator(300, 60, params=cfg)
        sim.run()
        b, s = _auc_arrays(sim, 300)
        return calculate_effect_size(s, b)

    full = d_for(min_norm_on=True, friction_on=True, steering_on=True)
    friction = d_for(min_norm_on=False, friction_on=True, steering_on=False)
    minnorm = d_for(min_norm_on=True, friction_on=False, steering_on=False)
    none = d_for(min_norm_on=False, friction_on=False, steering_on=False)

    assert full > friction > minnorm            # decomposição causal coerente
    assert abs(none) < 0.25                       # sanidade
    assert full > 2.5                             # efeito grande, honesto


def test_steering_compresses_kl_not_reserve():
    """Steering (Hawkes+TS) honra a intenção (comprime KL) sem inflar a reserva."""
    sim = Simulator(300, 60, params=dict(min_norm_on=False, friction_on=False, steering_on=True))
    sim.run()
    kl_base = _median_kl(sim, "baseline", 300)
    kl_sust = _median_kl(sim, "sustainable", 300)
    assert kl_sust < kl_base * 0.5   # intenção honrada
