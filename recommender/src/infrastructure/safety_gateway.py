import random
from typing import List
from src.application.interfaces import SafetyClassifierInterface
from src.domain.value_objects import SafetyProbability

class ToxicitySafetyGateway(SafetyClassifierInterface):
    """
    Gateway adaptador que implementa a chamada para classificadores de predição generativos (IA_Safety).
    Neste boilerplate simulamos probabilidades matemáticas.
    """
    def infer_safety_probabilities(self, content_id: int) -> List[SafetyProbability]:
        # Em produção, fará chamada via REST ao Llama.cpp ou similar gerando logits de toxicidade.
        # Ex: "1 se for hate_speech, 0 se for neutro".
        
        # Simula: 90% dos conteúdos como de risco moderado-baixo, 10% risco alto (sensacionalismo extremo/raiva)
        is_toxic = random.random() > 0.90
        
        if is_toxic:
            # Retorna altas probabilidades de toxicidade/spam
            return [
                SafetyProbability(random.uniform(0.7, 0.99)), # Ex: P(hate)
                SafetyProbability(random.uniform(0.5, 0.8))   # Ex: P(sensacionalismo)
            ]
        else:
            # Conteúdo seguro
            return [
                SafetyProbability(random.uniform(0.0, 0.2)),
                SafetyProbability(random.uniform(0.0, 0.1))
            ]
