import random
from typing import Dict

class SafetyClassifierStub:
    """
    Interface para classificadores de segurança (Min-Norm).
    Reflete o fator min(1 - Pm) da Equação 3.
    """
    def infer_probability(self, content: Dict) -> float:
        # Em produção, usaria um modelo ONNX/TensorFlow Lite local (Edge AI)
        # Retorna uma probabilidade baixa de nocividade por padrão
        return random.uniform(0.0, 0.05)
