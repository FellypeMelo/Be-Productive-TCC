from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from src.inference.hawkes_classifier import HawkesClassifier

router = APIRouter()

_hawkes = HawkesClassifier(
    alpha1=0.8, beta1=0.5,   # System 1
    alpha2=0.5, beta2=0.01,  # System 2
)

class HawkesAnalysisRequest(BaseModel):
    user_id: int
    event_intervals: List[float]  # seconds between consecutive interactions

class HawkesAnalysisResponse(BaseModel):
    user_id: int
    system: int  # 1 or 2
    ratio: float  # lambda_s1 / lambda_s2
    lambda_s1: float
    lambda_s2: float

@router.post("/behavior/analyze", response_model=HawkesAnalysisResponse)
async def analyze_behavior(req: HawkesAnalysisRequest):
    """
    Analyze user interaction patterns via Hawkes dual-kernel process (Eq. 2).
    Classifies as System 1 (impulsive) or System 2 (deliberative).
    """
    if not req.event_intervals:
        raise HTTPException(status_code=400, detail="event_intervals required")

    result = _hawkes.classify(req.event_intervals)
    return HawkesAnalysisResponse(
        user_id=req.user_id,
        system=result["system"],
        ratio=result["ratio"],
        lambda_s1=result["lambda_s1"],
        lambda_s2=result["lambda_s2"],
    )


from src.domain.math_models import calculate_hyperbolic_discount


class HyperbolicDiscountRequest(BaseModel):
    user_id: int
    value: float  # Intrinsic value V
    delay: float  # Time delay D (minutes)
    k: float = 0.5  # Impulsivity constant


class HyperbolicDiscountResponse(BaseModel):
    user_id: int
    perceived_value: float
    discount_factor: float


@router.post("/behavior/hyperbolic-discount", response_model=HyperbolicDiscountResponse)
async def compute_hyperbolic_discount(req: HyperbolicDiscountRequest):
    """
    Calculate perceived value via hyperbolic discounting (Eq. 5).
    V_p = V / (1 + k * D)
    """
    pv = calculate_hyperbolic_discount(req.value, req.k, req.delay)
    return HyperbolicDiscountResponse(
        user_id=req.user_id,
        perceived_value=pv,
        discount_factor=pv / req.value if req.value > 0 else 0.0,
    )
