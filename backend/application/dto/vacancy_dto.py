from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from backend.domain.enums import (
    EmploymentType,
    SourceType,
    VacancyStatus,
    WorkMode,
)
from backend.domain.values import (
    ApplyScore,
    Confidence,
    Money,
    SalaryRange,
    ScamScore,
)

@dataclass
class CreateSourceDTO:
    name: str
    type: SourceType
    url: str

@dataclass
class CreateCompanyDTO:
    name: str
    website: Optional[str] = None
    description: Optional[str] = None

@dataclass
class CreateVacancyDTO:
    source_id: UUID
    external_id: str
    title: str
    url: str
    salary: SalaryRange
    description: str = ""
    company_id: Optional[UUID] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    work_mode: Optional[WorkMode] = None
    published_at: Optional[datetime] = None
    raw_data: Optional[dict] = None
    skill_names: Optional[list[str]] = None

@dataclass
class UpdateVacancyDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    work_mode: Optional[WorkMode] = None
    status: Optional[VacancyStatus] = None
    company_id: Optional[UUID] = None
    salary: Optional[SalaryRange] = None
    raw_data: Optional[dict] = None
    skill_names: Optional[list[str]] = None

@dataclass
class MetricDTO:
    salary_min: Optional[Money]
    salary_max: Optional[Money]
    scam_score: ScamScore
    apply_score: ApplyScore
    confidence: Confidence
    details: dict

@dataclass
class VacancyWithMetricDTO:
    vacancy_id: UUID
    title: str
    url: str
    status: VacancyStatus
    metric: Optional[MetricDTO]

