from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

class CompanyCreateRequest(BaseModel):
    name: str = Field(..., max_length=255)
    website: str | None = Field(default=None, max_length=1024)
    description: str | None = None

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    website: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

