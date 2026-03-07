from typing import List, Optional
from src.application.interfaces import ContentRepositoryInterface, SafetyClassifierInterface, ContentItem
from src.domain.math_models import calculate_quality_score

class RecommendationUseCase:
    def __init__(self, repo: ContentRepositoryInterface, safety_clf: SafetyClassifierInterface):
        self.repo = repo
        self.safety_classifier = safety_clf

    def generate_recommendations(
        self, 
        user_id: int, 
        limit: int = 20, 
        absolute_mode_active: bool = False, 
        declared_goal: Optional[str] = None
    ) -> List[ContentItem]:
        candidates = self.repo.get_candidate_contents()
        
        for item in candidates:
            # Algoritmo 4: Modo Absoluto 
            if absolute_mode_active and item.category != declared_goal:
                item.perceived_value = 0.0
                continue
                
            # Aplica o Agregador Min-Norm de Qualidade (Equação 3)
            probs = self.safety_classifier.infer_safety_probabilities(item.content_id)
            quality = calculate_quality_score(item.base_score, probs)
            
            # The tests expect quality.value, which comes from the Value Object
            item.perceived_value = quality.value 
            item.base_score = quality.value

        # Filter items with non-zero perceived value and sort
        valid_items = [i for i in candidates if i.perceived_value > 0.0]
        valid_items.sort(key=lambda x: x.perceived_value, reverse=True)
        
        return valid_items[:limit]
