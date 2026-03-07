from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.value_objects import SafetyProbability

class ContentItem:
    """Mock/DTO structure for content items passing through the application layer."""
    def __init__(self, content_id: int, category: str, base_score: float):
        self.content_id = content_id
        self.category = category
        self.base_score = base_score
        # Absolute mode zeroing check
        self.perceived_value = base_score 

class ContentRepositoryInterface(ABC):
    @abstractmethod
    def get_candidate_contents(self, category: Optional[str] = None) -> List[ContentItem]:
        """Fetch candidates from DB."""
        pass

class SafetyClassifierInterface(ABC):
    @abstractmethod
    def infer_safety_probabilities(self, content_id: int) -> List[SafetyProbability]:
        """Fetch multi-model safety probabilities (Predatory/Toxic metrics)."""
        pass

class TrajectoryRepositoryInterface(ABC):
    @abstractmethod
    def save_fatigue_parameters(self, user_id: int, mu_rest: float, kappa1: float, kappa2: float) -> None:
        """Sincroniza os parâmetros da EDO com o cliente Edge AI."""
        pass
    
    @abstractmethod
    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        """Verifica se o Edge AI disparou o sinal de fadiga crítica para frear sugestões."""
        pass
