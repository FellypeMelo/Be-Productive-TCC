"""Recommendation endpoints (Strict SRP and DI)"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Literal

from src.application.recommendation_use_case import RecommendationUseCase
from src.application.fatigue_use_case import FatigueUseCase
from src.infrastructure.repositories import MySQLContentRepository
from src.infrastructure.safety_gateway import ToxicitySafetyGateway
from src.infrastructure.hybrid_scorer import HybridScorer
from src.infrastructure.behavioral_trajectory_repo import BehavioralTrajectoryRepository
from src.inference.hawkes_classifier import HawkesClassifier

router = APIRouter()

class RecommendRequest(BaseModel):
    """Request schema for recommendations (RF014)"""
    user_id: int
    category: Optional[Literal["PRODUTIVIDADE", "ENTRETENIMENTO"]] = None
    topic_id: Optional[int] = None
    limit: int = 20
    # Added Absolute Mode Support
    absolute_mode_active: bool = False
    declared_goal: Optional[str] = None

class RecommendResponse(BaseModel):
    """Response schema for recommendations"""
    content_ids: List[int]
    scores: List[float]
    model_version: str
    friction_level: Optional[str] = None  # NEW: from fatigue policy

class ThompsonResponse(BaseModel):
    user_id: int
    selected_arm: str  # "system_1" or "system_2"
    alpha_s2: float
    beta_s2: float

# Dependency Injection Builders
_hybrid_scorer = HybridScorer()
_trajectory_repo = BehavioralTrajectoryRepository(
)

def get_recommendation_use_case():
    repo = MySQLContentRepository(hybrid_scorer=_hybrid_scorer)
    safety_gateway = ToxicitySafetyGateway()
    hawkes_clf = HawkesClassifier(
        alpha1=0.8, beta1=0.5,    # System 1: high arousal, fast decay
        alpha2=0.5, beta2=0.01,   # System 2: moderate arousal, slow decay
    )
    return RecommendationUseCase(repo, safety_gateway, hawkes_clf)

def get_fatigue_use_case():
    return FatigueUseCase(_trajectory_repo)

@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest, use_case: RecommendationUseCase = Depends(get_recommendation_use_case)):
    """
    Get personalized content recommendations for a user.

    Adheres to the Clean Architecture:
    - Injecting safety gate (Algoritmo 2 - Min Aggregation Risk)
    - Applying Absolute Mode if enabled (Algoritmo 4)
    """
    try:
        results = use_case.generate_recommendations(
            user_id=request.user_id,
            limit=request.limit,
            absolute_mode_active=request.absolute_mode_active,
            declared_goal=request.declared_goal
        )

        # Check fatigue policy (Algorithm 3)
        fatigue_uc = get_fatigue_use_case()
        friction = fatigue_uc.get_friction_policy(request.user_id)

        return RecommendResponse(
            content_ids=[item.content_id for item in results],
            scores=[item.perceived_value for item in results],
            model_version="1.1.0-PaperCompliant",
            friction_level=friction.value,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/{user_id}")
async def recommend_get(
    user_id: int,
    limit: int = 20,
    use_case: RecommendationUseCase = Depends(get_recommendation_use_case)
):
    """GET version for simple recommendations"""
    try:
        results = use_case.generate_recommendations(user_id=user_id, limit=limit)

        # Check fatigue policy
        fatigue_uc = get_fatigue_use_case()
        friction = fatigue_uc.get_friction_policy(user_id)

        return {
            "content_ids": [item.content_id for item in results],
            "scores": [item.perceived_value for item in results],
            "model_version": "1.1.0-PaperCompliant",
            "friction_level": friction.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/thompson/{user_id}", response_model=ThompsonResponse)
async def thompson_sampling_endpoint(user_id: int, use_case: RecommendationUseCase = Depends(get_recommendation_use_case)):
    """
    Thompson Sampling (Eq. 2 Bayesian arm selection).
    Returns which system the model should optimize for this timestep.
    """
    is_s2 = use_case.should_explore_deliberative(user_id)
    return ThompsonResponse(
        user_id=user_id,
        selected_arm="system_2" if is_s2 else "system_1",
        alpha_s2=use_case._ts_alpha_s2,
        beta_s2=use_case._ts_beta_s2,
    )
