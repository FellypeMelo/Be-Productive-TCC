import re
from typing import List
from src.application.interfaces import ContentItem, SafetyClassifierInterface
from src.domain.value_objects import SafetyProbability

SAFETY_DIMENSIONS = [
    "hate_speech",         # P1
    "misinformation",      # P2
    "violent_content",     # P3
    "clickbait",           # P4
    "compulsive_stimuli",  # P5
]

_LEXICONS = {
    "hate_speech": {"inferior", "exterminar", "sub-humano", "odio"},
    "misinformation": {"cura garantida", "verdade escondida", "sem provas", "conspiracao"},
    "violent_content": {"matar", "massacre", "tortura", "violencia grafica"},
    "clickbait": {"voce nao vai acreditar", "chocante", "imperdivel", "segredo revelado"},
    "compulsive_stimuli": {"role sem parar", "infinito", "agora ou nunca", "nao pare"},
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


class ToxicitySafetyGateway(SafetyClassifierInterface):
    """
    Gateway for the 5 IA_Safety classifiers (min-norm aggregation, Eq. 3).

    Transparent lexical baseline over actual content. It is deterministic,
    auditable and replaceable by ONNX models behind the same interface.
    """
    def __init__(self, toxic_ratio: float = 0.10):
        self._toxic_ratio = toxic_ratio

    def infer_safety_probabilities(self, content_id: int) -> List[SafetyProbability]:
        return [SafetyProbability(0.05) for _ in SAFETY_DIMENSIONS]

    def infer_content_probabilities(self, item: ContentItem) -> List[SafetyProbability]:
        text = _normalize(" ".join((item.title, item.body, item.tags)))
        probabilities: List[SafetyProbability] = []
        for dimension in SAFETY_DIMENSIONS:
            hits = sum(1 for phrase in _LEXICONS[dimension] if phrase in text)
            probability = min(0.99, 0.05 + 0.45 * hits)
            probabilities.append(SafetyProbability(probability))
        return probabilities
