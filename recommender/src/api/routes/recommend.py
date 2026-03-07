"""Recommendation endpoints (Strict SRP and DI)"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Literal

from src.application.recommendation_use_case import RecommendationUseCase
from src.infrastructure.repositories import MySQLContentRepository
from src.infrastructure.safety_gateway import ToxicitySafetyGateway

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

# Dependency Injection Builders
def get_recommendation_use_case():
    repo = MySQLContentRepository()
    safety_gateway = ToxicitySafetyGateway()
    return RecommendationUseCase(repo, safety_gateway)

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
        
        return RecommendResponse(
            content_ids=[item.content_id for item in results],
            scores=[item.perceived_value for item in results],
            model_version="1.1.0-PaperCompliant"
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
        
        return {
            "content_ids": [item.content_id for item in results],
            "scores": [item.perceived_value for item in results],
            "model_version": "1.1.0-PaperCompliant"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
