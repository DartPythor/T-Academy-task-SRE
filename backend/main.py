from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.infrastructure.db.migrations import run_migrations
from backend.infrastructure.db.session import engine
from backend.infrastructure.logging import get_logger
from backend.infrastructure.middleware.correlation_id import CorrelationIDMiddleware
from backend.presentation.api.router import api_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    logger.info("Application starting", version=settings.app_version)

    # Автоматическое применение миграций Alembic.
    # В docker-образе миграции применяет entrypoint, поэтому там
    # VA_RUN_MIGRATIONS=false, чтобы не выполнять их дважды.
    if settings.run_migrations:
        try:
            await asyncio.to_thread(run_migrations)
        except Exception as exc:
            logger.error("Failed to apply database migrations", error=str(exc))
            raise
    else:
        logger.info("Database migrations are applied by the entrypoint, skipping")

    yield
    logger.info("Application shutting down")
    await engine.dispose()

def create_app() -> FastAPI:
    """Фабрика FastAPI-приложения."""

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        docs_url=settings.api_docs_url,
        lifespan=lifespan,
    )

    app.add_middleware(CorrelationIDMiddleware)

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.exception_handler(Exception)
    async def unhandled_exception(request, exc):
        corr_id = getattr(request.state, "correlation_id", "unknown")
        logger.exception(
            "Unhandled exception",
            correlation_id=corr_id,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app

app = create_app()
