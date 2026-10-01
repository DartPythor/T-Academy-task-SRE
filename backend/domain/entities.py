from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from backend.domain.enums import SourceType, VacancyStatus, WorkMode, EmploymentType
from backend.domain.metrics import VacancyMetric

@dataclass
class Source:
    id: UUID
    name: str
    type: SourceType
    url: str
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, name: str, type: SourceType, url: str) -> "Source":
        return cls(id=uuid4(), name=name, type=type, url=url)

    def disable(self) -> None:
        self.enabled = False
        self.updated_at = datetime.now(timezone.utc)

    def enable(self) -> None:
        self.enabled = True
        self.updated_at = datetime.now(timezone.utc)

@dataclass
class Company:
    id: UUID
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, name: str, website: Optional[str] = None) -> "Company":
        return cls(id=uuid4(), name=name, website=website)

@dataclass(frozen=True)
class Skill:
    id: UUID
    name: str

    @classmethod
    def create(cls, name: str) -> "Skill":
        return cls(id=uuid4(), name=name.strip().lower())

@dataclass
class Vacancy:
    id: UUID
    source_id: UUID
    external_id: str
    title: str
    url: str
    description: str = ""
    company_id: Optional[UUID] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    work_mode: Optional[WorkMode] = None
    published_at: Optional[datetime] = None
    status: VacancyStatus = VacancyStatus.NEW
    raw_data: dict = field(default_factory=dict)
    skills: list[Skill] = field(default_factory=list)
    metric: Optional[VacancyMetric] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        source_id: UUID,
        external_id: str,
        title: str,
        url: str,
        description: str = "",
        company_id: Optional[UUID] = None,
        location: Optional[str] = None,
        employment_type: Optional[EmploymentType] = None,
        work_mode: Optional[WorkMode] = None,
        published_at: Optional[datetime] = None,
        raw_data: Optional[dict] = None,
    ) -> "Vacancy":
        return cls(
            id=uuid4(),
            source_id=source_id,
            external_id=external_id,
            title=title,
            url=url,
            description=description,
            company_id=company_id,
            location=location,
            employment_type=employment_type,
            work_mode=work_mode,
            published_at=published_at,
            raw_data=raw_data or {},
        )

    def add_skill(self, skill: Skill) -> None:
        if skill not in self.skills:
            self.skills.append(skill)
            self._touch()

    def remove_skill(self, skill: Skill) -> None:
        if skill in self.skills:
            self.skills.remove(skill)
            self._touch()

    def attach_metric(self, metric: VacancyMetric) -> None:
        if metric.vacancy_id != self.id:
            raise ValueError("metric belongs to another vacancy")
        self.metric = metric
        self.status = VacancyStatus.PROCESSED
        self._touch()

    def archive(self) -> None:
        self.status = VacancyStatus.ARCHIVED
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

