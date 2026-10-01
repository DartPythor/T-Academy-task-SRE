from __future__ import annotations

import logging
import sys

def configure_logging(level: str = "INFO") -> None:
    """Настройка структурированного JSON-логирования.

    Все логи пишутся в stdout как JSON-строки для корректной обработки
    системами сбора логов (Loki, Datadog, ELK и т.д.).

    В debug-режиме использует человекочитаемый формат для локальной разработки.

    Factor 11: Treat logs as event streams.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level.upper())

    class SimpleJSONFormatter(logging.Formatter):
        """Форматтер, выводящий логи как JSON-строки."""

        def format(self, record: logging.LogRecord) -> str:
            import json
            from datetime import datetime, timezone

            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            corr_id = getattr(record, "correlation_id", None)
            if corr_id:
                log_entry["correlation_id"] = corr_id

            if record.exc_info and record.exc_info[0]:
                log_entry["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_entry, default=str)

    handler.setFormatter(SimpleJSONFormatter())
    root_logger.addHandler(handler)

    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if level.upper() == "INFO" else level.upper()
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Получить логгер с именем модуля."""
    return logging.getLogger(name)
