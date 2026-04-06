import numpy as np
import copy
from src.abm.agent import generate_population
from src.domain.math_models import calculate_ego_depletion, calculate_hawkes_activation, thompson_sampling_choice
from src.domain.value_objects import AttentionReserve

class Simulator:
    """ABM Game Engine comparing Baseline against the proposed Value-Aligned RecSys."""
    def __init__(self, num_agents: int = 1000, time_steps: int = 100, params: dict = None):
        self.num_agents = num_agents
        self.time_steps = time_steps
        self.params = params or {}
        self.agents = generate_population(num_agents)
        
        # Result dictionary storing R-curves and Q-matrices for KL divergence
        self.results = {
            "baseline": {
                "r_curves": [[] for _ in range(num_agents)],
                "q_allocations": [np.zeros(2) for _ in range(num_agents)],
                "hawkes_ratios": [[] for _ in range(num_agents)]
            },
            "sustainable": {
                "r_curves": [[] for _ in range(num_agents)],
                "q_allocations": [np.zeros(2) for _ in range(num_agents)],
                "hawkes_ratios": [[] for _ in range(num_agents)]
            }
        }
        
    def _run_model_step(self, t: int, model: str, agent, idx: int, state_override: float):
        """Simula timestep t sob a mecânica do modelo selecionado"""
        reserve = AttentionReserve(current=state_override, r_max=agent.r_max)
        
        if model == "baseline":
            # Traditional feeds optimize for reactivity. High scroll velocity (v), rapid context switching.
            v_scroll = max(0.0, self.params.get("v_scroll_base", np.random.normal(150, 20)))
            v_alt = max(0.0, np.random.normal(5, 1))
            # Hardcoded intention hijack - the feed feeds random fast content
            cat_idx = np.random.choice([0, 1], p=[0.2, 0.8])
        else:
            # Sustainable feed slows down scroll and focuses on explicit intent
            # Applying reduction factor if provided
            reduction = self.params.get("v_scroll_reduction", 0.66) # Default ~3x slow
            v_scroll = max(0.0, self.params.get("v_scroll_sust", np.random.normal(150 * (1 - reduction), 10)))
            v_alt = max(0.0, np.random.normal(1, 0.5))
            # Thompson Sampling (Eq. 2 — bayesian arm selection)
            ts_alpha_prod = self.params.get("ts_alpha_prod", 10.0)
            ts_beta_prod = self.params.get("ts_beta_prod", 1.0)
            if agent.declared_intent == "PRODUTIVIDADE":
                cat_idx = thompson_sampling_choice(
                    alpha_s1=ts_alpha_prod, beta_s1=ts_beta_prod,
                    alpha_s2=ts_beta_prod, beta_s2=ts_alpha_prod
                )
            else:
                cat_idx = thompson_sampling_choice(
                    alpha_s1=ts_beta_prod, beta_s1=ts_alpha_prod,
                    alpha_s2=ts_alpha_prod, beta_s2=ts_beta_prod
                )
            
        # Ego Depletion formula (Eq 4): dR/dt = μ_rest·(R_max - R) - L(X,t)
        k1 = self.params.get("k1", 0.1)
        k2 = self.params.get("k2", 0.5)
        mu_rest = 0.0 if model == "baseline" else self.params.get("mu_rest", 0.1)
        new_reserve = calculate_ego_depletion(reserve, v_scroll, v_alt, k1=k1, k2=k2, delta_t=1.0, mu_rest=mu_rest)

        # Hawkes (Eq. 2): lambda_s1 = alpha1 * exp(-beta1 * dt), lambda_s2 = alpha2 * exp(-beta2 * dt)
        alpha1 = agent.k * self.params.get("alpha1_scale", 0.8)
        alpha2 = self.params.get("alpha2", 0.5)
        beta1 = self.params.get("beta1", 0.5)
        beta2 = self.params.get("beta2", 0.01)
        lambda_s1 = calculate_hawkes_activation(alpha=alpha1, beta=beta1, time_delta=float(t + 1))
        lambda_s2 = calculate_hawkes_activation(alpha=alpha2, beta=beta2, time_delta=float(t + 1))
        hawkes_ratio = lambda_s1 / max(lambda_s2, 1e-12)
        self.results[model]["hawkes_ratios"][idx].append(hawkes_ratio)
        self.results[model]["r_curves"][idx].append(new_reserve.current)
        
        # Add Time Allocation (Continuous time unit spent instead of discrete to avoid Binomial clustering)
        time_spent = max(0.1, np.random.normal(1.0, 0.2))
        self.results[model]["q_allocations"][idx][cat_idx] += time_spent
        
        return new_reserve.current

    def run(self):
        """Runs the N-agent iteration simultaneously for Baseline and Sustainable"""
        for i, agent in enumerate(self.agents):
            current_r_base = agent.current_reserve
            current_r_sust = agent.current_reserve
            
            for t in range(self.time_steps):
                current_r_base = self._run_model_step(t, "baseline", agent, i, current_r_base)
                current_r_sust = self._run_model_step(t, "sustainable", agent, i, current_r_sust)
