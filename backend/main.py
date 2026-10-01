from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.infrastructure.db.session import engine
from backend.infrastructure.logging import configure_logging, get_logger
from backend.infrastructure.middleware.correlation_id import CorrelationIDMiddleware
from backend.presentation.api.router import api_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения (12 Factor: Disposability).

    Таблицы БД создаются через Alembic миграции, не на старте.
    """
    logger.info("Application starting", extra={"version": settings.app_version})
    yield
    logger.info("Application shutting down")
    await engine.dispose()

def create_app() -> FastAPI:
    """Фабрика FastAPI-приложения."""

    configure_logging(settings.log_level)

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
            extra={"correlation_id": corr_id, "path": str(request.url)},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app

app = create_app()
