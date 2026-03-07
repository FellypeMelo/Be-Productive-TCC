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
    
    # 5 agents, each should have a list of length 5 (t=0, t=1, t=2, t=3, t=4)
    baseline_rcruve_agent_0 = simulator.results["baseline"]["r_curves"][0]
    assert len(baseline_rcruve_agent_0) == 5
    
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
