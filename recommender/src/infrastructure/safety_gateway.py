import random
from typing import List
from src.application.interfaces import SafetyClassifierInterface
from src.domain.value_objects import SafetyProbability

SAFETY_DIMENSIONS = [
    "hate_speech",         # P1
    "misinformation",      # P2
    "violent_content",     # P3
    "clickbait",           # P4
    "compulsive_stimuli",  # P5
]

class ToxicitySafetyGateway(SafetyClassifierInterface):
    """
    Gateway for the 5 IA_Safety classifiers (min-norm aggregation, Eq. 3).
    In production, each dimension would be an ONNX/Llama.cpp classifier.
    Currently simulated with calibrated probability distributions.
    """
    def __init__(self, toxic_ratio: float = 0.10):
        self._toxic_ratio = toxic_ratio

    def infer_safety_probabilities(self, content_id: int) -> List[SafetyProbability]:
        is_toxic = random.random() < self._toxic_ratio

        if is_toxic:
            return [
                SafetyProbability(random.uniform(0.7, 0.99)),  # P1: hate_speech
                SafetyProbability(random.uniform(0.6, 0.90)),  # P2: misinformation
                SafetyProbability(random.uniform(0.5, 0.85)),  # P3: violent_content
                SafetyProbability(random.uniform(0.4, 0.75)),  # P4: clickbait
                SafetyProbability(random.uniform(0.5, 0.80)),  # P5: compulsive_stimuli
            ]
        else:
            return [
                SafetyProbability(random.uniform(0.0, 0.20)),  # P1
                SafetyProbability(random.uniform(0.0, 0.15)),  # P2
                SafetyProbability(random.uniform(0.0, 0.10)),  # P3
                SafetyProbability(random.uniform(0.0, 0.25)),  # P4
                SafetyProbability(random.uniform(0.0, 0.20)),  # P5
            ]
