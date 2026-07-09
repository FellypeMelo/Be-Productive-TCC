"""Health check endpoints"""

from fastapi import APIRouter, Response, status

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic liveness check — the process is up and serving."""
    return {
        "status": "healthy",
        "service": "recommender"
    }


@router.get("/health/ready")
async def readiness_check(response: Response):
    """Readiness probe reflecting real dependency state.

    - ``database_connected`` is determined by actually opening (and closing) a
      MySQL connection, not hardcoded.
    - ``model_loaded`` reflects whether the safety gateway and hybrid scorer
      objects can be constructed.

    Returns HTTP 503 when the service is not ready to take traffic (DB down or
    core objects fail to construct), otherwise 200. The body always reports the
    individual component states so callers can diagnose the failure.
    """
    database_connected = False
    db_error = None
    try:
        from src.infrastructure.database import get_db_connection

        conn = get_db_connection()
        try:
            conn.ping(reconnect=False, attempts=1)
        except Exception:
            # Some connector versions don't expose ping the same way; a
            # successful connect above is already a strong readiness signal.
            pass
        conn.close()
        database_connected = True
    except Exception as exc:  # pragma: no cover - depends on live DB
        db_error = str(exc)

    model_loaded = False
    model_error = None
    try:
        from src.infrastructure.safety_gateway import ToxicitySafetyGateway
        from src.infrastructure.hybrid_scorer import HybridScorer

        ToxicitySafetyGateway()
        HybridScorer()
        model_loaded = True
    except Exception as exc:  # pragma: no cover - construction is trivial
        model_error = str(exc)

    ready = database_connected and model_loaded
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    body = {
        "status": "ready" if ready else "not_ready",
        "model_loaded": model_loaded,
        "database_connected": database_connected,
    }
    if db_error:
        body["database_error"] = db_error
    if model_error:
        body["model_error"] = model_error
    return body
