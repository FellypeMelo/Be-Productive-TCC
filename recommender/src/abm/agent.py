import numpy as np

class SyntheticAgent:
    def __init__(self, agent_id: int, mu: float, k: float, r_max: float, declared_intent: str):
        self.agent_id = agent_id
        self.mu = mu
        self.k = k
        self.r_max = r_max
        self.current_reserve = r_max
        self.declared_intent = declared_intent

def generate_population(N: int = 1000):
    """
    Gera uma população de agentes sintéticos seguindo distribuições log-normais (AI-XP).
    Não contém dados empíricos reais, garantindo compliance total com RGPD/LGPD.
    """
    np.random.seed(42) # Replicability for ABM
    
    # Parâmetros sob log normal para modelagem clínica
    mus = np.random.lognormal(mean=0.5, sigma=0.2, size=N)
    impulsivities = np.random.lognormal(mean=-1.0, sigma=0.5, size=N)
    r_maxs = np.random.normal(loc=100.0, scale=15.0, size=N)
    
    intents = np.random.choice(["PRODUTIVIDADE", "ENTRETENIMENTO"], size=N, p=[0.7, 0.3])
    
    agents = []
    for i in range(N):
        agents.append(SyntheticAgent(
            agent_id=i,
            mu=mus[i],
            k=impulsivities[i],
            r_max=max(50.0, r_maxs[i]), # floor it to 50
            declared_intent=intents[i]
        ))
        
    return agents
