import numpy as np


class SyntheticAgent:
    def __init__(self, agent_id: int, mu: float, k: float, r_max: float, declared_intent: str):
        self.agent_id = agent_id
        self.mu = mu
        self.k = k
        self.r_max = r_max
        self.current_reserve = r_max
        self.declared_intent = declared_intent

    @property
    def intent_dist(self):
        """Distribuição de intenção declarada P sobre [PRODUTIVIDADE, ENTRETENIMENTO].

        Usada como referência da Divergência KL (intenção declarada vs consumo real).
        Mesmo usuários voltados a entretenimento retêm alguma intenção produtiva.
        """
        if self.declared_intent == "PRODUTIVIDADE":
            return np.array([0.85, 0.15])
        return np.array([0.30, 0.70])


def generate_population(N: int = 1000, seed: int = 42, rng=None):
    """Gera população de agentes sintéticos sob distribuições log-normais (AI-XP).

    Não contém dados empíricos reais, garantindo conformidade total com RGPD/LGPD.
    Aceita um `rng` (np.random.Generator) injetável para reprodutibilidade estrita;
    na ausência, usa um gerador semeado por `seed`.
    """
    if rng is None:
        rng = np.random.default_rng(seed)

    # Parâmetros clínicos sob log-normal / normal
    mus = rng.lognormal(mean=0.5, sigma=0.2, size=N)
    impulsivities = rng.lognormal(mean=-1.0, sigma=0.5, size=N)
    r_maxs = rng.normal(loc=100.0, scale=15.0, size=N)
    intents = rng.choice(["PRODUTIVIDADE", "ENTRETENIMENTO"], size=N, p=[0.7, 0.3])

    agents = []
    for i in range(N):
        agents.append(
            SyntheticAgent(
                agent_id=i,
                mu=float(mus[i]),
                k=float(impulsivities[i]),
                r_max=float(max(50.0, r_maxs[i])),  # piso em 50
                declared_intent=str(intents[i]),
            )
        )

    return agents
