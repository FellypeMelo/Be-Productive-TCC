import math
from typing import List, Dict

class HawkesClassifier:
    """
    Classificador leve que infere ativação do Sistema 1 ou 2 baseado na latência.
    Reflete a Equação 2 do artigo (kernels duals).
    """
    def __init__(self, alpha1: float = 1.0, alpha2: float = 0.5, beta1: float = 0.5, beta2: float = 0.01):
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.beta1 = beta1
        self.beta2 = beta2

    def classify(self, event_intervals: List[float]) -> Dict[str, any]:
        if not event_intervals:
            return {"system": 2, "ratio": 0.0}
            
        # Calcula intensidade média para cada kernel baseado no delay médio
        avg_delay = sum(event_intervals) / len(event_intervals)
        
        lambda_s1 = self.alpha1 * math.exp(-self.beta1 * avg_delay)
        lambda_s2 = self.alpha2 * math.exp(-self.beta2 * avg_delay)
        
        ratio = lambda_s1 / max(lambda_s2, 1e-12)
        
        return {
            "system": 1 if ratio >= 1.0 else 2,
            "ratio": ratio,
            "lambda_s1": lambda_s1,
            "lambda_s2": lambda_s2
        }
