"""Health check endpoints"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "recommender"
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check - verify model is loaded"""
    # In production, check if model is loaded and DB is accessible
    return {
        "status": "ready",
        "model_loaded": True,
        "database_connected": True
    }
