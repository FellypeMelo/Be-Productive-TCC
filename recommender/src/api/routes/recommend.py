"""Recommendation endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Literal

from src.inference.predictor import get_recommendations

router = APIRouter()


class RecommendRequest(BaseModel):
    """Request schema for recommendations (RF014)"""
    user_id: int
    category: Optional[Literal["PRODUTIVIDADE", "ENTRETENIMENTO"]] = None
    topic_id: Optional[int] = None
    limit: int = 20
    emotional_state: Optional[str] = None


class RecommendResponse(BaseModel):
    """Response schema for recommendations"""
    content_ids: List[int]
    scores: List[float]
    model_version: str


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    Get personalized content recommendations for a user.
    
    Uses hybrid recommendation combining:
    - Content-based filtering (topic similarity)
    - Collaborative filtering (user behavior)
    - Quality score weighting (RN002)
    - Well-being adjustments
    """
    try:
        result = get_recommendations(
            user_id=request.user_id,
            category=request.category,
            topic_id=request.topic_id,
            limit=request.limit,
            emotional_state=request.emotional_state
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/{user_id}")
async def recommend_get(
    user_id: int,
    category: Optional[str] = None,
    topic_id: Optional[int] = None,
    limit: int = 20
):
    """GET version for simple recommendations"""
    try:
        result = get_recommendations(
            user_id=user_id,
            category=category,
            topic_id=topic_id,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
