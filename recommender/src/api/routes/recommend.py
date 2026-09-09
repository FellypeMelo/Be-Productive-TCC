"""Recommendation endpoints (Strict SRP and DI)"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Literal

from src.application.recommendation_use_case import RecommendationUseCase
from src.infrastructure.repositories import MySQLContentRepository
from src.infrastructure.safety_gateway import ToxicitySafetyGateway
from src.infrastructure.hybrid_scorer import HybridScorer
from src.inference.hawkes_classifier import HawkesClassifier
from src.api.deps import get_fatigue_use_case
from src.application.experiments import (
    ALGORITHM_VERSION,
    ASSIGNMENT_VERSION,
    EXPERIMENT_ID,
    experiment_assignment,
)

router = APIRouter()

class RecommendRequest(BaseModel):
    """Request schema for recommendations (RF014)"""
    user_id: int = Field(gt=0)
    category: Optional[Literal["PRODUTIVIDADE", "ENTRETENIMENTO"]] = None
    topic_id: Optional[int] = Field(default=None, gt=0)
    limit: int = Field(default=20, ge=1, le=50)
    # Added Absolute Mode Support
    absolute_mode_active: bool = False
    declared_goal: Optional[Literal["PRODUTIVIDADE", "ENTRETENIMENTO"]] = None
    # Binary order computed on-device. Raw fatigue telemetry is never sent.
    protective_mode_active: bool = False
    # Separate opt-in for research participation; product personalization is
    # intentionally independent from this flag.
    research_consent: bool = False

class RecommendResponse(BaseModel):
    """Response schema for recommendations"""
    content_ids: List[int]
    scores: List[float]
    model_version: str
    friction_level: Optional[str] = None  # NEW: from fatigue policy
    experiment: str
    experiment_id: str
    assignment_version: str
    variant: str
    eligible: bool
    algorithm_version: str
    explanations: Dict[int, List[str]]

class ThompsonResponse(BaseModel):
    user_id: int
    selected_arm: str  # "system_1" or "system_2"
    alpha_s2: float
    beta_s2: float

# Dependency Injection Builders
_hybrid_scorer = HybridScorer()
_recommendation_use_case = RecommendationUseCase(
    MySQLContentRepository(hybrid_scorer=_hybrid_scorer),
    ToxicitySafetyGateway(),
    HawkesClassifier(alpha1=0.8, beta1=0.5, alpha2=0.5, beta2=0.01),
)

def get_recommendation_use_case():
    return _recommendation_use_case

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
            declared_goal=request.declared_goal,
            category=request.category,
            topic_id=request.topic_id,
            protective_mode_active=request.protective_mode_active,
            research_consent=request.research_consent,
        )

        # Check fatigue policy (Algorithm 3)
        fatigue_uc = get_fatigue_use_case()
        friction = fatigue_uc.get_friction_policy(request.user_id)

        assignment = experiment_assignment(request.user_id, request.research_consent)
        return RecommendResponse(
            content_ids=[item.content_id for item in results],
            scores=[item.perceived_value for item in results],
            model_version=ALGORITHM_VERSION,
            friction_level=friction.value,
            experiment=str(assignment["variant"]),
            experiment_id=EXPERIMENT_ID,
            assignment_version=ASSIGNMENT_VERSION,
            variant=str(assignment["variant"]),
            eligible=bool(assignment["eligible"]),
            algorithm_version=ALGORITHM_VERSION,
            explanations={item.content_id: item.explanations for item in results},
        )
    except Exception:
        raise HTTPException(status_code=503, detail="recommendation service unavailable")


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
            "model_version": ALGORITHM_VERSION,
            "friction_level": friction.value,
            "experiment": "not_eligible",
            "experiment_id": EXPERIMENT_ID,
            "assignment_version": ASSIGNMENT_VERSION,
            "variant": "not_eligible",
            "eligible": False,
            "algorithm_version": ALGORITHM_VERSION,
            "explanations": {item.content_id: item.explanations for item in results},
        }
    except Exception:
        raise HTTPException(status_code=503, detail="recommendation service unavailable")


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
