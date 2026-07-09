import hashlib
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

# Per-dimension probability ranges for higher-risk ("toxic") vs. safe content.
# Kept identical to the previous calibrated bands so downstream min-norm
# aggregation (Eq. 3) behaves the same — only the source of randomness changed.
_TOXIC_RANGES = [
    (0.70, 0.99),  # P1: hate_speech
    (0.60, 0.90),  # P2: misinformation
    (0.50, 0.85),  # P3: violent_content
    (0.40, 0.75),  # P4: clickbait
    (0.50, 0.80),  # P5: compulsive_stimuli
]
_SAFE_RANGES = [
    (0.00, 0.20),  # P1
    (0.00, 0.15),  # P2
    (0.00, 0.10),  # P3
    (0.00, 0.25),  # P4
    (0.00, 0.20),  # P5
]


def _hash_unit_float(content_id: int, salt: str) -> float:
    """Deterministic pseudo-feature in [0, 1] derived from (content_id, salt).

    Uses SHA-256 so the value is stable across processes and Python runs
    (unlike the salted builtin ``hash`` for strings). The same inputs always
    yield the same float — this is what makes the gateway reproducible.
    """
    digest = hashlib.sha256(f"{content_id}:{salt}".encode("utf-8")).digest()
    raw = int.from_bytes(digest[:8], "big")
    return raw / float(2**64 - 1)


class ToxicitySafetyGateway(SafetyClassifierInterface):
    """
    Gateway for the 5 IA_Safety classifiers (min-norm aggregation, Eq. 3).

    In production each dimension would be an ONNX / llama.cpp classifier. This
    is a DETERMINISTIC stand-in, not random: every dimension's probability is a
    stable function of the ``content_id`` (a per-content seed). The same
    ``content_id`` therefore yields identical probabilities on every call,
    which lets the min-norm safety aggregation operate on a consistent signal
    instead of per-request noise (random values made Eq. 3 non-reproducible and
    untestable). Real classifiers can be dropped in behind the same interface.

    Roughly ``toxic_ratio`` (default ~10%) of content ids hash into the
    higher-risk band; the rest stay in the low-probability safe band.
    """
    def __init__(self, toxic_ratio: float = 0.10):
        self._toxic_ratio = toxic_ratio

    def infer_safety_probabilities(self, content_id: int) -> List[SafetyProbability]:
        # Stable toxic/safe decision: ~toxic_ratio of ids fall below the cut.
        is_toxic = _hash_unit_float(content_id, "toxic") < self._toxic_ratio
        ranges = _TOXIC_RANGES if is_toxic else _SAFE_RANGES

        probs: List[SafetyProbability] = []
        for dim, (lo, hi) in zip(SAFETY_DIMENSIONS, ranges):
            u = _hash_unit_float(content_id, dim)
            value = lo + u * (hi - lo)
            # Clamp defensively; construction stays within [0, 1] by design.
            value = min(1.0, max(0.0, value))
            probs.append(SafetyProbability(value))
        return probs
