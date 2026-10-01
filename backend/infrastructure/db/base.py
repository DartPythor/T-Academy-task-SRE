from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase

def utcnow() -> datetime:
    """Единая точка получения текущего времени в UTC."""
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    """Базовый declarative-класс для всех ORM-моделей."""
    pass
