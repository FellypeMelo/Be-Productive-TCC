import pytest
import numpy as np
# Will fail before implementation
from src.abm.engine import Simulator

def test_engine_initializes_two_environments():
    simulator = Simulator(num_agents=10, time_steps=5)
    
    assert simulator.num_agents == 10
    assert simulator.time_steps == 5
    assert len(simulator.agents) == 10
    
    # Needs to store R(t) curve for every agent for both models
    assert "baseline" in simulator.results
    assert "sustainable" in simulator.results
    
def test_simulation_generates_r_curve():
    """Garante que a simulação avança t passos e os salva na matriz."""
    simulator = Simulator(num_agents=5, time_steps=4)
    simulator.run()
    
    # 5 agents, each should have a list of length 4 (t=0, t=1, t=2, t=3)
    baseline_rcruve_agent_0 = simulator.results["baseline"]["r_curves"][0]
    assert len(baseline_rcruve_agent_0) == 4
    
    # As the baseline consumes the user more aggressively, it should be lower than sustainable
    baseline_final_r = simulator.results["baseline"]["r_curves"][0][-1]
    sustainable_final_r = simulator.results["sustainable"]["r_curves"][0][-1]
    
    # Assert divergence exists, without deterministic precision since it's stochastic
    assert baseline_final_r <= sustainable_final_r

def test_simulation_yields_q_arrays_for_kl():
    """Valida se o motor computa o Vetor Q (tempo alocado real) para KL Divergence"""
    simulator = Simulator(num_agents=2, time_steps=10)
    simulator.run()
    
    q_baseline = simulator.results["baseline"]["q_allocations"][0]
    assert len(q_baseline) == 2 # Productivity, Entertainment sums
    assert np.sum(q_baseline) > 0 # Some time must have been spent

def test_engine_uses_hawkes_for_s1_s2_classification():
    """
    FASE RED — Grupo 3: engine deve calcular lambda_s1 e lambda_s2
    via Hawkes (Eq. 2) a cada timestep e registrar as razões
    lambda_s1/lambda_s2 em results[model]["hawkes_ratios"].
    """
    simulator = Simulator(num_agents=5, time_steps=4)
    simulator.run()

    for model in ["baseline", "sustainable"]:
        assert "hawkes_ratios" in simulator.results[model], \
            f"results['{model}'] missing 'hawkes_ratios'"

        ratios = simulator.results[model]["hawkes_ratios"]
        assert len(ratios) == 5, "Uma lista por agente"

        for agent_ratios in ratios:
            assert len(agent_ratios) == 4, "Um ratio por timestep"
            for r in agent_ratios:
                # 0 é válido: passos iniciais sem eventos do Sistema 1 dão λ_s1 = 0.
                assert r >= 0, "Ratio lambda_s1/lambda_s2 deve ser não-negativo"

def test_integration_sustainable_aligns_with_declared_intent():
    """
    Grupo 6: Teste de integração completo.
    O modelo sustentável deve alocar significativamente mais tempo
    na categoria da intenção declarada que o baseline.
    """
    from src.abm.stats import calculate_p_value

    simulator = Simulator(num_agents=50, time_steps=20)
    simulator.run()

    alignment_baseline = []
    alignment_sustainable = []

    for i, agent in enumerate(simulator.agents):
        target_idx = 0 if agent.declared_intent == "PRODUTIVIDADE" else 1

        q_base = simulator.results["baseline"]["q_allocations"][i]
        total_base = max(sum(q_base), 1e-12)
        alignment_baseline.append(q_base[target_idx] / total_base)

        q_sust = simulator.results["sustainable"]["q_allocations"][i]
        total_sust = max(sum(q_sust), 1e-12)
        alignment_sustainable.append(q_sust[target_idx] / total_sust)

    import numpy as np
    align_b = np.array(alignment_baseline)
    align_s = np.array(alignment_sustainable)

    # Sustainable deve ter alinhamento médio > 80%
    assert np.mean(align_s) > 0.80

    # Sustainable deve ter alinhamento maior que baseline
    assert np.mean(align_s) > np.mean(align_b)

    # Diferença deve ser estatisticamente significativa
    p_val = calculate_p_value(align_s, align_b)
    assert p_val < 0.05

