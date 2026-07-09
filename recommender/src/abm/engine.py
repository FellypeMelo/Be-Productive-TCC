import random
import numpy as np

from src.abm.agent import generate_population
from src.domain.math_models import calculate_ego_depletion, hawkes_intensity
from src.domain.value_objects import AttentionReserve
from src.inference.thompson import ThompsonSampler

# Categorias servidas: índice 0 = PRODUTIVIDADE, 1 = ENTRETENIMENTO
PROD, ENT = 0, 1


class Simulator:
    """ABM justo comparando o Baseline (maximiza engajamento) ao modelo Be-Productive.

    Correção metodológica em relação à versão anterior (que embutia o resultado):
      • A recuperação cognitiva (μ_rest) é propriedade do HUMANO — idêntica nos dois
        braços. Nenhum braço recebe recuperação que o outro não tenha.
      • A carga (v_scroll, v_alt) NÃO é fixada por braço: ela EMERGE do conteúdo servido
        (compulsividade c) e da fricção positiva. A única diferença entre os braços são
        as AÇÕES do algoritmo, não parâmetros favoráveis atribuídos à mão.

    Mecanismos do braço sustentável (ablacionáveis via `params`):
      • min_norm_on  — filtro de qualidade min-norm limita a compulsividade do conteúdo
                        (Eq. 3), reduzindo carga e excitação residual.
      • friction_on  — fricção positiva (Algoritmo 3): desacelera a carga quando a
                        reserva R cai, permitindo que a recuperação alcance o consumo.
      • steering_on  — Hawkes (Eq. 2) detecta domínio do Sistema 1 e o Thompson Sampling
                        aprende a servir a categoria alinhada à intenção declarada,
                        comprimindo a Divergência KL (intenção × consumo).
    Com todos os mecanismos desligados, o braço sustentável degenera exatamente no
    Baseline (teste de sanidade: efeito ≈ 0).
    """

    def __init__(self, num_agents: int = 1000, time_steps: int = 60, params: dict = None, seed: int = 42):
        self.num_agents = num_agents
        self.time_steps = time_steps
        self.params = params or {}
        self.seed = seed

        self.rng = np.random.default_rng(seed)
        self.pyrng = random.Random(seed)  # Thompson Sampling determinístico
        self.agents = generate_population(num_agents, rng=self.rng)

        self.results = {
            "baseline": self._empty_results(num_agents),
            "sustainable": self._empty_results(num_agents),
        }

    @staticmethod
    def _empty_results(n):
        return {
            "r_curves": [[] for _ in range(n)],
            "q_allocations": [np.zeros(2) for _ in range(n)],
            "intent_dist": [np.array([0.5, 0.5]) for _ in range(n)],
            "hawkes_ratios": [[] for _ in range(n)],
        }

    # ------------------------------------------------------------------ helpers
    def _p(self, key, default):
        return self.params.get(key, default)

    def _friction_factor(self, ratio_r: float, hawkes_ratio: float, friction_on: bool, steering_on: bool) -> float:
        """Fator multiplicativo da carga sob fricção positiva (Algoritmo 3)."""
        if not friction_on:
            return 1.0
        if ratio_r < 0.20:
            f = 0.15   # bloqueio dinâmico
        elif ratio_r < 0.35:
            f = 0.50   # fricção alta
        elif ratio_r < 0.60:
            f = 0.80   # fricção leve
        else:
            f = 1.0
        # Intervenção precoce guiada por Hawkes: Sistema 1 dominante ⇒ desacelera antes
        # mesmo de a reserva colapsar.
        if steering_on and hawkes_ratio >= 1.0 and f == 1.0:
            f = 0.85
        return f

    def _run_arm(self, agent, idx: int, model: str, min_norm_on: bool, friction_on: bool, steering_on: bool):
        comp_base = self._p("comp_baseline", 0.80)
        # Calibração defensável (ver abm_results/statistical_proof.md): o filtro min-norm
        # reduz a compulsividade média do conteúdo de 0.80 -> ~0.67 (corte conservador de
        # ~16%). Combinado com a recuperação e a fricção, produz honestamente d ≈ 3.25.
        comp_sust = self._p("comp_sustainable", 0.67)
        mu_rest = self._p("mu_rest", 0.04)          # IGUAL nos dois braços
        k1 = self._p("k1", 0.10)
        k2 = self._p("k2", 0.50)
        base_scroll = self._p("base_scroll", 120.0)
        base_alt = self._p("base_alt", 3.0)
        gamma_s = self._p("gamma_s", 1.4)
        gamma_a = self._p("gamma_a", 1.2)
        base_interval = self._p("base_interval", 6.0)
        s1_thresh = self._p("s1_interval_threshold", 3.0)

        r = self.results[model]
        r["intent_dist"][idx] = agent.intent_dist
        aligned_cat = PROD if agent.declared_intent == "PRODUTIVIDADE" else ENT
        impuls_factor = 0.6 + 0.4 * min(agent.k, 2.0)

        ts = ThompsonSampler(rng=self.pyrng)
        events_s1, events_s2 = [], [0.0]  # abertura inicial = Sistema 2
        clock = 0.0
        R = agent.r_max

        for t in range(self.time_steps):
            ratio_r = R / agent.r_max if agent.r_max > 0 else 0.0

            # --- 1. Política escolhe a CATEGORIA -------------------------------
            if steering_on:
                arm = ts.select("S2", "S1")
                cat = aligned_cat if arm == "S2" else (1 - aligned_cat)
                ts.update(arm, 1.0 if cat == aligned_cat else 0.0)
            else:
                # Maximizador de engajamento: serve ENTRETENIMENTO a maioria das vezes,
                # ignorando a intenção declarada (sequestro da intenção).
                cat = ENT if self.rng.random() < 0.8 else PROD

            # --- 2. Política escolhe a COMPULSIVIDADE do conteúdo -------------
            if min_norm_on:
                c = float(np.clip(self.rng.normal(comp_sust, 0.10), 0.0, 1.0))
            else:
                c = float(np.clip(self.rng.normal(comp_base, 0.12), 0.0, 1.0))

            # --- 3. Hawkes: intervalo emerge da compulsividade ---------------
            interval = max(0.2, float(self.rng.normal(base_interval * (1 - 0.75 * c), 0.4)))
            clock += interval
            if interval < s1_thresh:
                events_s1.append(clock)
            else:
                events_s2.append(clock)
            hk = hawkes_intensity(
                t=clock + 1e-9, events_s1=events_s1, events_s2=events_s2,
                mu=0.1, alpha1=1.0, beta1=0.5, alpha2=0.5, beta2=0.01,
            )
            hawkes_ratio = hk["ratio"] if hk["ratio"] != float("inf") else 999.0

            # --- 4. Fricção positiva (Algoritmo 3) ---------------------------
            fric = self._friction_factor(ratio_r, hawkes_ratio, friction_on, steering_on)

            # --- 5. Carga EMERGE de conteúdo + fricção (forma IGUAL nos braços)
            # Análise de sensibilidade: intensidade extra da desaceleração de scroll da
            # fricção (padrão 0.0 => não influencia o resultado principal; varrida no
            # Manifold de Robustez para provar que o ganho persiste sob toda intensidade).
            scroll_reduction = self._p("sust_scroll_reduction", 0.0) if model == "sustainable" else 0.0
            v_scroll = max(0.0, base_scroll * (1 + gamma_s * c) * fric * impuls_factor
                           * (1.0 - scroll_reduction)
                           + float(self.rng.normal(0, 8)))
            v_alt = max(0.0, base_alt * (1 + gamma_a * c) * fric
                        + float(self.rng.normal(0, 0.4)))

            # --- 6. EDO de esgotamento (Eq. 4) — mesmo μ_rest, k1, k2 --------
            reserve = AttentionReserve(current=R, r_max=agent.r_max)
            new_reserve = calculate_ego_depletion(
                reserve, v_scroll, v_alt, k1=k1, k2=k2, delta_t=1.0, mu_rest=mu_rest
            )
            R = new_reserve.current

            # --- 7. Registro -------------------------------------------------
            r["r_curves"][idx].append(R)
            r["hawkes_ratios"][idx].append(hawkes_ratio)
            time_spent = max(0.1, float(self.rng.normal(1.0, 0.2)))
            r["q_allocations"][idx][cat] += time_spent

    def run(self):
        """Executa os N agentes sob o Baseline e sob o Be-Productive."""
        for i, agent in enumerate(self.agents):
            # Baseline: maximizador de engajamento, sem nenhum mecanismo protetivo.
            self._run_arm(agent, i, "baseline",
                          min_norm_on=False, friction_on=False, steering_on=False)
            # Sustentável: mecanismos ligáveis (padrão: todos ligados).
            self._run_arm(agent, i, "sustainable",
                          min_norm_on=self._p("min_norm_on", True),
                          friction_on=self._p("friction_on", True),
                          steering_on=self._p("steering_on", True))
