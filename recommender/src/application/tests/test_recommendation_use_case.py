import pytest
from src.application.interfaces import ContentItem, ContentRepositoryInterface, SafetyClassifierInterface
from src.domain.value_objects import SafetyProbability
# This will fail to import until GREEN phase
from src.application.recommendation_use_case import RecommendationUseCase

class MockContentRepo(ContentRepositoryInterface):
    def get_candidate_contents(self, category=None):
        return [
            ContentItem(1, "PRODUTIVIDADE", 0.8),
            ContentItem(2, "ENTRETENIMENTO", 0.9),
            ContentItem(3, "PRODUTIVIDADE", 0.5)
        ]

class MockSafetyClassifier(SafetyClassifierInterface):
    def infer_safety_probabilities(self, content_id):
        if content_id == 2:
            return [SafetyProbability(0.9), SafetyProbability(0.8)] # Toxic!
        return [SafetyProbability(0.1), SafetyProbability(0.05)] # Safe

def test_recommendation_applies_min_aggregation_penalty():
    """Testa se o Use Case aplica a matemática do domínio penalizando o item 2 e rebaixando ele no rank."""
    repo = MockContentRepo()
    safety_classifier = MockSafetyClassifier()
    
    use_case = RecommendationUseCase(repo, safety_classifier)
    recommendations = use_case.generate_recommendations(user_id=1, limit=3)
    
    # Item 2 originally had a base score of 0.9.
    # Its penalty min(1-0.9, 1-0.8) = min(0.1, 0.2) = 0.1
    # Final quality score for Item 2 = 0.9 * 0.1 = 0.09
    
    # Item 1 has 0.8 * min(0.9, 0.95) = 0.8 * 0.9 = 0.72
    
    # The first recommendation should be Item 1 now, not Item 2.
    assert recommendations[0].content_id == 1
    assert recommendations[2].content_id == 2

def test_absolute_mode_blinds_out_of_category_content():
    """Algoritmo 4: Engenharia de Pré-Comprometimento. Força Perceived Value = 0."""
    repo = MockContentRepo()
    safety_classifier = MockSafetyClassifier()
    
    use_case = RecommendationUseCase(repo, safety_classifier)
    
    # Activating absolute mode for "PRODUTIVIDADE"
    recommendations = use_case.generate_recommendations(
        user_id=1, 
        limit=3, 
        absolute_mode_active=True, 
        declared_goal="PRODUTIVIDADE"
    )
    
    for rec in recommendations:
        if rec.category != "PRODUTIVIDADE":
            assert rec.perceived_value == 0.0
            
    # Item 2 is ENTRETENIMENTO, so its perceived value should be stripped out or it shouldn't even be recommended.
    assert all(rec.category == "PRODUTIVIDADE" for rec in recommendations if rec.perceived_value > 0)
