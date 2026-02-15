"""
Prediction/Inference module
Handles model loading and generating recommendations
"""

from typing import Optional, List, Dict, Any
import numpy as np

from src.models.hybrid import HybridRecommender
from src.domain.metrics import calculate_quality_score
from src.infrastructure.database import get_all_content_ids


# Global model instance (loaded once)
_model: Optional[HybridRecommender] = None
MODEL_VERSION = "1.0.0"


def get_model() -> HybridRecommender:
    """Get or initialize the recommendation model"""
    global _model
    if _model is None:
        _model = HybridRecommender()
        # In production, load pre-trained model weights here
        # _model.load("models/current/model.pkl")
    return _model


def get_recommendations(
    user_id: int,
    category: Optional[str] = None,
    limit: int = 20,
    emotional_state: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate personalized recommendations for a user.
    
    Args:
        user_id: The user to recommend for
        category: Optional category filter (PRODUTIVIDADE or ENTRETENIMENTO)
        limit: Maximum number of recommendations
        emotional_state: User's current emotional state for adjustments
    
    Returns:
        Dict with content_ids, scores, and model_version
    """
    model = get_model()
    
    # Get candidate content IDs from DB (UC14)
    try:
        candidate_ids = get_all_content_ids(category=category)
    except Exception as e:
        print(f"Error fetching candidate IDs from DB: {e}")
        candidate_ids = []

    if not candidate_ids:
        # Fallback to local range if DB is empty or failed
        candidate_ids = list(range(1, 101))
    
    # Get predictions from hybrid model
    content_ids, scores = model.predict(
        user_id=user_id,
        candidate_ids=candidate_ids,
        category=category
    )
    
    # Apply well-being adjustments based on emotional state
    if emotional_state:
        scores = apply_wellbeing_adjustments(scores, emotional_state)
    
    # Sort by score and limit
    sorted_indices = np.argsort(scores)[::-1][:limit]
    
    final_ids = [content_ids[i] for i in sorted_indices]
    final_scores = [float(scores[i]) for i in sorted_indices]
    
    return {
        "content_ids": final_ids,
        "scores": final_scores,
        "model_version": MODEL_VERSION
    }


def apply_wellbeing_adjustments(
    scores: np.ndarray,
    emotional_state: str
) -> np.ndarray:
    """
    Adjust recommendation scores based on user's emotional state.
    
    - If stressed/negative: boost calming content, reduce high-energy
    - If positive: slight diversity boost
    """
    adjustments = {
        "ESTRESSADO": 0.8,  # Reduce intensity
        "NEGATIVO": 0.9,    # Slight reduction
        "POSITIVO": 1.0,    # No change
        "NEUTRO": 1.0       # No change
    }
    
    factor = adjustments.get(emotional_state, 1.0)
    return scores * factor
