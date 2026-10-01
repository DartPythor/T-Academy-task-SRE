from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")

class PaginationParams(BaseModel):
    limit: int = 50
    offset: int = 0

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None

class HealthResponse(BaseModel):
    status: str = "ok"
    database: str = "unknown"
    timestamp: datetime = datetime.now()

