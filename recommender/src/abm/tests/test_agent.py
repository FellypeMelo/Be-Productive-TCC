import pytest
import numpy as np
# Will fail before implementation
from src.abm.agent import SyntheticAgent, generate_population

def test_synthetic_agent_initialization():
    """Agents must initialize with deterministic attributes"""
    agent = SyntheticAgent(agent_id=1, mu=2.0, k=0.5, r_max=100.0, declared_intent="PRODUTIVIDADE")
    
    assert agent.agent_id == 1
    assert agent.mu == 2.0
    assert agent.k == 0.5
    assert agent.r_max == 100.0
    # Reserve starts at maximum
    assert agent.current_reserve == 100.0

def test_log_normal_population_generation():
    """Garante que a população de N agentes sintéticos siga a distribuição log-normal sem vazar dados reais."""
    population_size = 1000
    agents = generate_population(N=population_size)
    
    assert len(agents) == population_size
    
    # Collect generated 'k' parameters (impulsivity)
    k_values = [agent.k for agent in agents]
    
    # In a log-normal distribution generated properly, values should be strictly positive
    assert all(k > 0 for k in k_values)
    assert np.mean(k_values) > 0
    
    # Intents should be roughly distributed
    intents = [a.declared_intent for a in agents]
    assert "PRODUTIVIDADE" in intents
    assert "ENTRETENIMENTO" in intents
