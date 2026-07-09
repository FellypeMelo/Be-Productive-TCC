"""Injeção de dependência compartilhada da API.

Antes, `recommend.py` e `fatigue.py` construíam CADA UM o seu próprio
`BehavioralTrajectoryRepository()`. A telemetria caía numa instância e o feed lia a
fricção de OUTRA — logo o `friction_level` do feed era eternamente `NONE`. Centralizar
o singleton aqui garante que os dois caminhos compartilhem o mesmo estado de fadiga.
"""
import os
from typing import Optional

from fastapi import Header, HTTPException, status

from src.application.fatigue_use_case import FatigueUseCase
from src.infrastructure.behavioral_trajectory_repo import BehavioralTrajectoryRepository

# Fonte única de verdade do estado de fadiga por usuário (processo único).
trajectory_repo = BehavioralTrajectoryRepository()


def get_fatigue_use_case() -> FatigueUseCase:
    return FatigueUseCase(trajectory_repo)


def require_internal_auth(
    x_internal_auth: Optional[str] = Header(default=None),
) -> None:
    """Shared-secret guard for internal-only endpoints.

    These endpoints (recommend / fatigue / behavior) are called only by the Go
    gateway now that fatigue is computed on-device — never by the browser. We
    gate them behind a shared secret carried in the `X-Internal-Auth` header.

    Behaviour is driven by the ``RECOMMENDER_SHARED_SECRET`` env var:
      * unset/empty  -> dev mode, all requests allowed (default; keeps tests green)
      * set          -> the request header must match exactly, else HTTP 401

    The env var is read on every call so it can be toggled without re-import.
    """
    secret = os.getenv("RECOMMENDER_SHARED_SECRET", "").strip()
    if not secret:
        return  # dev mode: no secret configured -> open
    if x_internal_auth != secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Internal-Auth header",
        )
