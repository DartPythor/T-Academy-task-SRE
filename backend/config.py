from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

from backend.infrastructure.logging import configure_logging

class Settings(BaseSettings):
    """Настройки приложения. Читаются из переменных окружения с префиксом VA_.

    Все секреты (пароли, токены) — ТОЛЬКО из переменных окружения.
    Для локальной разработки скопировать .env.example в .env.
    """

    app_title: str = "Vacancy Analyzer API"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    # Формат вывода логов: "json" (для сбора в Victoria Logs) или "console".
    log_format: str = "json"

    db_dsn: str = ""

    # Применять миграции Alembic при старте приложения.
    # В docker образе миграции применяет entrypoint (docker/entrypoint.sh),
    # поэтому там флаг выставлен в false, чтобы не запускать их дважды.
    run_migrations: bool = True
    # Путь до alembic.ini. Пусто — файл ищется рядом с корнем проекта.
    alembic_config: str = ""

    api_prefix: str = "/api/v1"
    api_docs_url: str = "/docs"

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30

    model_config = SettingsConfigDict(
        env_prefix="VA_",
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _validate_required(self) -> "Settings":
        if not self.db_dsn:
            raise ValueError(
                "VA_DB_DSN must be set via environment variable or .env file"
            )
        return self

settings = Settings()

# Настраиваем structlog до создания логгеров в других модулях.
configure_logging(settings.log_level, settings.log_format)

