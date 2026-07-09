"""
Be-Productive Recommendation Engine
FastAPI application entry point
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.deps import require_internal_auth
from src.api.routes import recommend, health, fatigue, behavior

app = FastAPI(
    title="Be-Productive Recommender",
    description="Ethical recommendation engine for mental health-focused social network",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers.
# Health stays public (liveness/readiness probes). The recommend / fatigue /
# behavior routers are internal-only — reached solely by the Go gateway — so they
# sit behind the shared-secret guard (no-op in dev when the secret is unset).
_internal_only = [Depends(require_internal_auth)]

app.include_router(health.router, tags=["Health"])
app.include_router(
    recommend.router, prefix="/api/v1", tags=["Recommendations"], dependencies=_internal_only
)
app.include_router(
    fatigue.router, prefix="/api/v1", tags=["Fatigue"], dependencies=_internal_only
)
app.include_router(
    behavior.router, prefix="/api/v1", tags=["Behavior"], dependencies=_internal_only
)


@app.get("/")
async def root():
    return {
        "service": "Be-Productive Recommender",
        "version": "2.0.0",
        "status": "running"
    }
