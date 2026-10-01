from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from backend.domain.enums import Currency, EmploymentType, VacancyStatus, WorkMode

class MoneySchema(BaseModel):
    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: Currency

class SalaryRangeSchema(BaseModel):
    min_amount: MoneySchema | None = None
    max_amount: MoneySchema | None = None
    gross: bool | None = None

    @model_validator(mode="after")
    def _check_range(self) -> "SalaryRangeSchema":
        if self.min_amount and self.max_amount:
            if self.min_amount.currency != self.max_amount.currency:
                raise ValueError("currency mismatch")
            if self.min_amount.amount > self.max_amount.amount:
                raise ValueError("min_amount > max_amount")
        return self

class SkillSchema(BaseModel):
    id: UUID
    name: str

class VacancyCreateRequest(BaseModel):
    source_id: UUID
    external_id: str
    title: str = Field(..., max_length=512)
    url: str = Field(..., max_length=1024)
    salary: SalaryRangeSchema
    description: str = ""
    company_id: UUID | None = None
    company_name: str | None = None
    location: str | None = None
    employment_type: EmploymentType | None = None
    work_mode: WorkMode | None = None
    published_at: datetime | None = None
    raw_data: dict | None = None
    skill_names: list[str] | None = None

class VacancyUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=512)
    description: str | None = None
    url: str | None = Field(default=None, max_length=1024)
    location: str | None = None
    employment_type: EmploymentType | None = None
    work_mode: WorkMode | None = None
    status: VacancyStatus | None = None
    company_id: UUID | None = None
    salary: SalaryRangeSchema | None = None
    raw_data: dict | None = None
    skill_names: list[str] | None = None

class MetricResponse(BaseModel):
    salary_min: MoneySchema | None = None
    salary_max: MoneySchema | None = None
    scam_score: int = Field(ge=0, le=100)
    apply_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    details: dict = Field(default_factory=dict)
    calculated_at: datetime | None = None

class VacancyResponse(BaseModel):
    id: UUID
    source_id: UUID
    external_id: str
    title: str
    url: str
    description: str
    company_id: UUID | None = None
    location: str | None = None
    employment_type: str | None = None
    work_mode: str | None = None
    published_at: datetime | None = None
    status: VacancyStatus
    skills: list[SkillSchema] = Field(default_factory=list)
    metric: MetricResponse | None = None
    created_at: datetime
    updated_at: datetime

class RecalculateRequest(BaseModel):
    salary: SalaryRangeSchema

