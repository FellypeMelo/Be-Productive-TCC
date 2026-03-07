from dataclasses import dataclass

@dataclass
class QualityScore:
    """Score contínuo representando a utilidade inferida (0 a 1)."""
    value: float

    def __post_init__(self):
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(f"QualityScore must be between 0 and 1, got {self.value}")

@dataclass
class AttentionReserve:
    """EDO: Reserva Cognitiva do usuário."""
    current: float
    r_max: float

    def __post_init__(self):
        if self.current < 0.0 or self.current > self.r_max:
            raise ValueError("Attention reserve out of bounds")

@dataclass
class SafetyProbability:
    """P_m(i): Probabilidade gerativa de um conteúdo ser predatório."""
    value: float

    def __post_init__(self):
        if not (0.0 <= self.value <= 1.0):
            raise ValueError("Probability must be between 0 and 1")
