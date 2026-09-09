from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.value_objects import SafetyProbability

class ContentItem:
    """Content candidate plus observable ranking features."""
    def __init__(
        self,
        content_id: int,
        category: str,
        base_score: float,
        title: str = "",
        body: str = "",
        tags: str = "",
        quality_score: float = 0.5,
        topic_affinity: float = 0.0,
        age_hours: float = 0.0,
        positive_events: int = 0,
        negative_events: int = 0,
        impression_count: int = 0,
    ):
        self.content_id = content_id
        self.category = category
        self.base_score = base_score
        self.title = title
        self.body = body
        self.tags = tags
        self.quality_score = quality_score
        self.topic_affinity = topic_affinity
        self.age_hours = age_hours
        self.positive_events = positive_events
        self.negative_events = negative_events
        self.impression_count = impression_count
        # Derived locally by the ranker from content quality and textual depth.
        # It is not an engagement metric and never contains behavioral telemetry.
        self.attention_support = 0.0
        self.perceived_value = base_score
        self.explanations: list[str] = []

class ContentRepositoryInterface(ABC):
    @abstractmethod
    def get_candidate_contents(
        self,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        topic_id: Optional[int] = None,
    ) -> List[ContentItem]:
        """Fetch candidates from DB, optionally scored for user."""
        pass

class SafetyClassifierInterface(ABC):
    @abstractmethod
    def infer_safety_probabilities(self, content_id: int) -> List[SafetyProbability]:
        """Fetch multi-model safety probabilities (Predatory/Toxic metrics)."""
        pass

    def infer_content_probabilities(self, item: ContentItem) -> List[SafetyProbability]:
        """Analyze full content when adapter supports it; preserve old adapters."""
        return self.infer_safety_probabilities(item.content_id)

class TrajectoryRepositoryInterface(ABC):
    @abstractmethod
    def save_fatigue_parameters(self, user_id: int, mu_rest: float, kappa1: float, kappa2: float) -> None:
        """Sincroniza os parâmetros da EDO com o cliente Edge AI."""
        pass

    @abstractmethod
    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        """Verifica se o Edge AI disparou o sinal de fadiga crítica para frear sugestões."""
        pass

    @abstractmethod
    def set_fatigue_alarm(self, user_id: int, is_fatigued: bool) -> None:
        """Allows Edge AI client to set alarm status."""
        pass

    @abstractmethod
    def record_behavioral_event(self, user_id: int, v_scroll: float, v_alt: float) -> None:
        """Record a behavioral signal event."""
        pass

    @abstractmethod
    def get_recent_behavior(self, user_id: int, n: int = 10) -> list:
        """Retrieve recent behavioral events."""
        pass

    @abstractmethod
    def init_attention_reserve(self, user_id: int, r_max: float = 100.0) -> None:
        """Initialize R(t) = R_max for a new session."""
        pass

    @abstractmethod
    def get_attention_reserve(self, user_id: int) -> tuple:
        """Returns (current_reserve, r_max). Defaults to (r_max, r_max) if unset."""
        pass

    @abstractmethod
    def update_attention_reserve(self, user_id: int, current: float, r_max: float) -> None:
        """Persist the updated R(t) after EDO integration step."""
        pass

    @abstractmethod
    def get_fatigue_params(self, user_id: int) -> dict:
        """Returns {mu_rest, kappa1, kappa2} for the user. Defaults if unset."""
        pass


class HawkesClassifierInterface(ABC):
    @abstractmethod
    def classify(self, event_intervals: list) -> dict:
        """Classify user state as System 1 (impulsive) or System 2 (deliberative)."""
        pass
