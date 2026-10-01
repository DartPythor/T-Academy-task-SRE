from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.domain.enums import SourceType

class SourceCreateRequest(BaseModel):
    name: str = Field(..., max_length=255)
    type: SourceType
    url: str = Field(..., max_length=1024)

class SourceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    type: SourceType | None = None
    url: str | None = Field(default=None, max_length=1024)
    enabled: bool | None = None

class SourceResponse(BaseModel):
    id: UUID
    name: str
    type: SourceType
    url: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

