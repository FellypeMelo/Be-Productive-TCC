import random
from typing import Dict, Hashable, Optional


class ThompsonSampler:
    """Amostragem de Thompson real (bandit Bayesiano com posteriores Beta).

    A versão anterior amostrava de uma Beta(α,β) *fixa* — um lançamento de moeda
    enviesado que nunca aprendia. Thompson Sampling, por definição, mantém um
    posterior por braço e o ATUALIZA a cada recompensa observada:

        θ_a ~ Beta(α_a, β_a)          # amostra
        a* = argmax_a θ_a             # escolhe o braço
        (α_{a*}, β_{a*}) += (r, 1−r)  # atualiza com a recompensa r ∈ [0,1]

    No modelo Be-Productive os braços são os dois sistemas cognitivos: "S1"
    (impulsivo) e "S2" (deliberado). A recompensa é o alinhamento do resultado com a
    intenção declarada do usuário, de modo que o sistema aprende a favorecer o braço
    que preserva a agência — sem hard-coding do enviesamento.
    """

    def __init__(
        self,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        rng: Optional[random.Random] = None,
    ):
        self.arms: Dict[Hashable, Dict[str, float]] = {}
        self._prior = (prior_alpha, prior_beta)
        # RNG injetável => reprodutibilidade determinística (fecha a lacuna do módulo
        # `random` global nunca semeado).
        self._rng = rng or random

    def _ensure(self, arm: Hashable) -> None:
        if arm not in self.arms:
            a, b = self._prior
            self.arms[arm] = {"alpha": a, "beta": b}

    def select(self, *arms: Hashable) -> Hashable:
        """Amostra cada posterior e retorna o braço com maior θ."""
        if not arms:
            arms = tuple(self.arms.keys())
        if not arms:
            raise ValueError("no arms to select from")
        best, best_theta = None, -1.0
        for arm in arms:
            self._ensure(arm)
            theta = self._rng.betavariate(self.arms[arm]["alpha"], self.arms[arm]["beta"])
            if theta > best_theta:
                best, best_theta = arm, theta
        return best

    def update(self, arm: Hashable, reward: float) -> None:
        """Atualiza o posterior do braço com recompensa r ∈ [0,1]."""
        reward = max(0.0, min(1.0, reward))
        self._ensure(arm)
        self.arms[arm]["alpha"] += reward
        self.arms[arm]["beta"] += 1.0 - reward

    def mean(self, arm: Hashable) -> float:
        """Média posterior α/(α+β) — probabilidade estimada de sucesso do braço."""
        self._ensure(arm)
        a, b = self.arms[arm]["alpha"], self.arms[arm]["beta"]
        return a / (a + b)
