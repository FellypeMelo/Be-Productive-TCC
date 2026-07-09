import numpy as np
import itertools
from src.abm.engine import Simulator
from src.abm.metrics import calculate_auc
from src.abm.stats import calculate_p_value


class SensitivityEngine:
    """Executa varreduras de Monte Carlo para provar robustez algorítmica."""

    def run_sweep(self, N: int, T: int, param_grid: dict, fixed: dict = None):
        """Percorre todas as combinações de `param_grid` e extrai métricas agregadas.

        `fixed` fornece parâmetros constantes (idênticos em toda a varredura) — usado
        para ISOLAR um mecanismo (ex.: desligar min-norm/fricção e variar apenas a
        desaceleração de scroll) e reproduzir o Manifold de Robustez com um eixo
        interpretável.
        """
        fixed = fixed or {}
        keys, values = zip(*param_grid.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

        sweep_results = []
        for combo in combinations:
            params = {**fixed, **combo}
            sim = Simulator(num_agents=N, time_steps=T, params=params, seed=42)
            sim.run()

            base_aucs = [calculate_auc(sim.results["baseline"]["r_curves"][i], 1.0) for i in range(N)]
            sust_aucs = [calculate_auc(sim.results["sustainable"]["r_curves"][i], 1.0) for i in range(N)]

            delta = float(np.mean(sust_aucs) - np.mean(base_aucs))
            p_val = calculate_p_value(sust_aucs, base_aucs)

            entry = dict(combo)
            entry["mean_auc_delta"] = delta
            entry["p_value"] = p_val
            sweep_results.append(entry)

        return sweep_results
