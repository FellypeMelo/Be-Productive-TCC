"""
Be-Productive Recommendation Engine
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import recommend, health

app = FastAPI(
    title="Be-Productive Recommender",
    description="Ethical recommendation engine for mental health-focused social network",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(recommend.router, prefix="/api/v1", tags=["Recommendations"])


@app.get("/")
async def root():
    return {
        "service": "Be-Productive Recommender",
        "version": "1.0.0",
        "status": "running"
    }
