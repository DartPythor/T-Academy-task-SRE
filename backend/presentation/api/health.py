from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from backend.infrastructure.db.session import check_db_connection
from backend.presentation.schemas.common import HealthResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check с проверкой подключения к БД.

    12 Factor: Disposability — быстрый старт и gracefiul shutdown.
    """
    db_ok = await check_db_connection()
    return HealthResponse(
        status="ok",
        database="connected" if db_ok else "disconnected",
        timestamp=datetime.now(timezone.utc),
    )

