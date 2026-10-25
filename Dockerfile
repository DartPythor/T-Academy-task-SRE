# syntax=docker/dockerfile:1
#
# Образ backend-сервиса.
#
# Зависимости ставятся Poetry в .venv внутри образа. В runtime попадают
# только само окружение и код, поэтому в образе есть и `alembic`, и
# `alembic.ini`, и каталог alembic/ — миграции применяет docker/entrypoint.sh.
#
# Сборка:
#   docker build -t vacancy-analyzer .
#   docker build --build-arg VERSION=1.2.3 --build-arg GIT_SHA=$(git rev-parse --short HEAD) .

# ─────────────────────────── builder ───────────────────────────
FROM python:3.13-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VERSION=2.0.0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Сначала только манифесты — слой с зависимостями кешируется между сборками
COPY pyproject.toml poetry.lock ./

RUN python -m venv .venv \
    && poetry install --no-ansi --only main --no-root

# ─────────────────────────── runtime ───────────────────────────
FROM python:3.13-slim AS runtime

# Миграции применяет entrypoint (docker/entrypoint.sh), поэтому в lifespan
# приложения их запускать не нужно — иначе они выполнялись бы дважды.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    APP_ROOT=/app \
    HEALTHCHECK_URL=http://127.0.0.1:8000/api/v1/health \
    VA_RUN_MIGRATIONS=false \
    VA_ALEMBIC_CONFIG=/app/alembic.ini

WORKDIR /app

# libpq5 — runtime-библиотека для asyncpg/libpq
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Непривилегированный пользователь
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home app

# Готовое окружение из builder-слоя
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Код приложения и всё необходимое для Alembic
COPY --chown=app:app backend/ ./backend/
COPY --chown=app:app alembic/ ./alembic/
COPY --chown=app:app alembic.ini ./alembic.ini
COPY --chown=app:app docker/ ./docker/

RUN chmod +x /app/docker/entrypoint.sh \
    && rm -rf /app/alembic/__pycache__ /app/alembic/versions/__pycache__

ARG VERSION=0.1.0
ARG BUILD_DATE
ARG GIT_SHA

LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.revision=$GIT_SHA
LABEL org.opencontainers.image.title="Vacancy Analyzer API"
LABEL org.opencontainers.image.description="Service for vacancy analysis and metrics"

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS "${HEALTHCHECK_URL}" || exit 1

ENTRYPOINT ["/app/docker/entrypoint.sh"]

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
