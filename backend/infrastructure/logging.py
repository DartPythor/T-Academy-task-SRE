from __future__ import annotations

import logging

import structlog
from structlog.typing import EventDict, Processor

# Стабильное логическое имя сервиса (semantic convention `service.name`).
# Используется в Victoria Logs для фильтрации и группировки.
SERVICE_NAME = "backend"

# Рендер финальной строки в зависимости от выбранного формата.
LOGGER_PARSER: dict[str, Processor] = {
    "console": structlog.dev.ConsoleRenderer(),
    "json": structlog.processors.JSONRenderer(ensure_ascii=False, default=str),
}

# Сопоставление текстового уровня (из конфигурации) с числовым уровнем stdlib.
_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _add_service_name(
    _logger: logging.Logger,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Добавляет обязательное поле `service.name` в каждую запись."""
    event_dict.setdefault("service.name", SERVICE_NAME)
    return event_dict


def configure_logging(level: str = "INFO", log_format: str = "json") -> None:
    """Настраивает structlog в зависимости от формата и уровня логирования.

    Каждая запись проходит по цепочке процессоров и выводится в stdout:
    ``add_log_level`` → ``TimeStamper`` → ``service.name`` → ``format_exc_info``
    → ``EventRenamer`` (``event`` → ``message``) → рендер (json/console).

    Factor 11: Treat logs as event streams.
    """
    processors: list[Processor] = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_service_name,
        structlog.processors.format_exc_info,
        structlog.processors.EventRenamer("message"),
        LOGGER_PARSER[log_format],
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            _LEVELS.get(level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )

    # Сторонние библиотеки (sqlalchemy, httpx) пишут через stdlib logging —
    # приглушаем их, чтобы они не шумели рядом со структурированными логами.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """Получить structlog-логгер с привязанным именем модуля."""
    return structlog.get_logger().bind(logger=name)
