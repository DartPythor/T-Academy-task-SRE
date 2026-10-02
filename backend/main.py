from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

from backend.config import settings
from backend.infrastructure.db.session import engine
from backend.infrastructure.logging import configure_logging, get_logger
from backend.infrastructure.middleware.correlation_id import CorrelationIDMiddleware
from backend.presentation.api.router import api_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения."""
    logger.info("Application starting", extra={"version": settings.app_version})

    # Автоматическое применение миграций Alembic
    try:
        import asyncio
        cfg = AlembicConfig(Path(__file__).resolve().parent.parent / "alembic.ini")
        await asyncio.to_thread(alembic_command.upgrade, cfg, "head")
        logger.info("Database migrations applied successfully")
    except Exception as e:
        logger.error("Failed to apply database migrations", extra={"error": str(e)})
        raise

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
