import numpy as np
import itertools
from src.abm.engine import Simulator
from src.abm.metrics import calculate_auc
from src.abm.stats import calculate_p_value

class SensitivityEngine:
    """Executa varreduras de Monte Carlo para provar robustez algorítmica."""
    
    def run_sweep(self, N: int, T: int, param_grid: dict):
        """
        Percorre todas as combinações de parâmetros e extrai métricas agregadas.
        """
        keys, values = zip(*param_grid.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        sweep_results = []
        
        for params in combinations:
            sim = Simulator(num_agents=N, time_steps=T, params=params)
            sim.run()
            
            # Agrega AUCs
            base_aucs = [calculate_auc(sim.results["baseline"]["r_curves"][i], 1.0) for i in range(N)]
            sust_aucs = [calculate_auc(sim.results["sustainable"]["r_curves"][i], 1.0) for i in range(N)]
            
            delta = np.mean(sust_aucs) - np.mean(base_aucs)
            p_val = calculate_p_value(sust_aucs, base_aucs)
            
            result_entry = params.copy()
            result_entry["mean_auc_delta"] = delta
            result_entry["p_value"] = p_val
            
            sweep_results.append(result_entry)
            
        return sweep_results
