from typing import List, Dict
from src.domain.math_models import hawkes_intensity


class HawkesClassifier:
    """Infere dominância do Sistema 1 vs Sistema 2 via processo de Hawkes bi-kernel (Eq. 2).

    Diferente da versão anterior (que aplicava um único exp ao atraso médio), este
    classificador reconstrói a linha temporal dos eventos a partir dos intervalos,
    rotula cada evento como Sistema 1 (reengajamento rápido) ou Sistema 2 (retomada
    deliberada) pela latência que o precede, e então soma as contribuições de todo o
    histórico — a definição real de intensidade de um ponto auto-excitante.
    """

    def __init__(
        self,
        alpha1: float = 1.0,
        alpha2: float = 0.5,
        beta1: float = 0.5,
        beta2: float = 0.01,
        mu: float = 0.1,
        s1_interval_threshold: float = 3.0,
    ):
        # Sistema 1: salto forte, decaimento rápido. Sistema 2: salto moderado, traço longo.
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.beta1 = beta1
        self.beta2 = beta2
        self.mu = mu
        # Latência (s) abaixo da qual um evento é considerado impulsivo (Sistema 1).
        self.s1_interval_threshold = s1_interval_threshold

    def classify(self, event_intervals: List[float]) -> Dict[str, float]:
        if not event_intervals:
            return {"system": 2, "ratio": 0.0, "lambda_s1": 0.0, "lambda_s2": 0.0}

        # Reconstrói os instantes absolutos t_k a partir dos intervalos consecutivos.
        # Evento i (i>=1) é rotulado pela latência event_intervals[i-1] que o precede;
        # o primeiro acesso (abertura espontânea) pertence ao Sistema 2 (coberto por μ).
        events_s1: List[float] = []
        events_s2: List[float] = []
        t = 0.0
        events_s2.append(t)  # abertura inicial = retomada deliberada
        for gap in event_intervals:
            t += max(gap, 1e-9)
            if gap < self.s1_interval_threshold:
                events_s1.append(t)
            else:
                events_s2.append(t)

        now = t + 1e-9  # avalia a intensidade logo após o último evento
        res = hawkes_intensity(
            t=now,
            events_s1=events_s1,
            events_s2=events_s2,
            mu=self.mu,
            alpha1=self.alpha1,
            beta1=self.beta1,
            alpha2=self.alpha2,
            beta2=self.beta2,
        )
        ratio = res["ratio"]
        return {
            "system": 1 if ratio >= 1.0 else 2,
            "ratio": ratio,
            "lambda_s1": res["lambda_s1"],
            "lambda_s2": res["lambda_s2"],
        }
