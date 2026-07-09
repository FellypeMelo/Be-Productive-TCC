from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from src.application.fatigue_use_case import FatigueUseCase
from src.api.deps import trajectory_repo, get_fatigue_use_case
from src.domain.value_objects import FrictionLevel

router = APIRouter()

# --- Request/Response schemas ---

class FatigueAlarmRequest(BaseModel):
    """Edge AI client reports fatigue detection."""
    user_id: int
    is_fatigued: bool

class BehavioralEventRequest(BaseModel):
    """Client sends behavioral telemetry for fatigue calculation."""
    user_id: int
    v_scroll: float       # Scroll velocity (pixels/sec)
    v_alt_context: float  # Context switching frequency

class FrictionResponse(BaseModel):
    user_id: int
    friction_level: str
    action: str  # "none", "slow_down", "positive_friction"

class EdgeParamsRequest(BaseModel):
    """Sync Edge AI EDO parameters."""
    user_id: int
    mu_rest: float
    k1: float
    k2: float
    r_max: float = 100.0

# --- DI (singleton compartilhado com o roteador de recomendação) ---

_trajectory_repo = trajectory_repo

# --- Endpoints ---

@router.post("/fatigue/sync-alarm", response_model=FrictionResponse)
async def sync_fatigue_alarm(
    req: FatigueAlarmRequest,
    use_case: FatigueUseCase = Depends(get_fatigue_use_case),
):
    """
    POST: Edge AI client reports that user has crossed cognitive exhaustion threshold.
    Triggers positive friction policy (Algorithm 3).
    """
    _trajectory_repo.set_fatigue_alarm(req.user_id, req.is_fatigued)
    friction = use_case.get_friction_policy(req.user_id)

    return FrictionResponse(
        user_id=req.user_id,
        friction_level=friction.value,
        action="positive_friction" if friction in (FrictionLevel.HIGH, FrictionLevel.BLOCK) else "none",
    )

@router.get("/fatigue/policy/{user_id}", response_model=FrictionResponse)
async def get_friction_policy(
    user_id: int,
    use_case: FatigueUseCase = Depends(get_fatigue_use_case),
):
    """
    GET: Fetch current friction policy for a user.
    Used by frontend to decide whether to apply positive friction.
    """
    friction = use_case.get_friction_policy(user_id)
    return FrictionResponse(
        user_id=user_id,
        friction_level=friction.value,
        action="positive_friction" if friction in (FrictionLevel.HIGH, FrictionLevel.BLOCK) else "none",
    )

@router.post("/fatigue/sync-params")
async def sync_edge_params(
    req: EdgeParamsRequest,
    use_case: FatigueUseCase = Depends(get_fatigue_use_case),
):
    """Sync EDO parameters (mu_rest, k1, k2) from Edge AI client."""
    use_case.sync_edge_parameters(
        user_id=req.user_id,
        mu_rest=req.mu_rest,
        k1=req.k1,
        k2=req.k2,
        r_max=req.r_max,
    )
    return {"status": "ok"}

@router.post("/fatigue/telemetry")
async def record_telemetry(
    req: BehavioralEventRequest,
    use_case: FatigueUseCase = Depends(get_fatigue_use_case),
):
    """Record behavioral event for fatigue accumulation (Eq. 4)."""
    friction = use_case.record_telemetry_and_update_reserve(
        user_id=req.user_id,
        v_scroll=req.v_scroll,
        v_alt=req.v_alt_context,
        delta_t=1.0,
    )
    return {
        "status": "ok",
        "friction_level": friction.value,
    }
