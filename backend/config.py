from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    """Настройки приложения. Читаются из переменных окружения с префиксом VA_.

    Все секреты (пароли, токены) — ТОЛЬКО из переменных окружения.
    Для локальной разработки скопировать .env.example в .env.
    """

    app_title: str = "Vacancy Analyzer API"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    db_dsn: str = ""

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

