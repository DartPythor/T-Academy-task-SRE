"""Alembic environment configuration.

DSN берётся из настроек приложения (VA_DB_DSN), а не из alembic.ini —
секреты не хранятся в файлах конфигурации (12 Factor App: config).

Одновременный запуск миграций из нескольких реплик безопасен:
миграции выполняются под transaction-level advisory-локом PostgreSQL.
"""
from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ── sys.path: корень проекта должен быть импортируемым (backend.*) ──────────
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Значение по умолчанию — только для запуска из исходников.
# В контейнере VA_DB_DSN всегда задан через env_file/.env.
os.environ.setdefault(
    "VA_DB_DSN", "postgresql+asyncpg://user:pass@localhost:5432/dbname"
)

from backend.config import settings  # noqa: E402
from backend.infrastructure.db.base import Base  # noqa: E402
from backend.infrastructure.db import models  # noqa: E402,F401  (регистрация таблиц)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# advisory-лок: одна и та же константа во всех репликах приложения
_MIGRATION_LOCK_ID = 8123456789


def get_url() -> str:
    """URL подключения: приоритет у настроек приложения, затем alembic.ini."""
    dsn = settings.db_dsn or config.get_main_option("sqlalchemy.url") or ""
    if not dsn or dsn.startswith("driver://"):
        raise RuntimeError(
            "Не задан DSN базы данных. Установите переменную окружения VA_DB_DSN."
        )
    return dsn


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (генерация SQL без подключения к БД)."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Применяет миграции под advisory-локом (защита от гонки реплик)."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    is_postgresql = connection.dialect.name == "postgresql"

    if is_postgresql:
        # transaction-level lock: снимается автоматически при COMMIT/ROLLBACK
        connection.exec_driver_sql(f"SELECT pg_advisory_xact_lock({_MIGRATION_LOCK_ID})")

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode (async-движок)."""
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
