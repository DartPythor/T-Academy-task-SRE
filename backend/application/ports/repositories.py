from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from backend.domain.entities import (
    Company,
    Skill,
    Source,
    Vacancy,
    VacancyMetric,
)

class SourceRepository(ABC):
    @abstractmethod
    async def get(self, source_id: UUID) -> Optional[Source]: ...

    @abstractmethod
    async def list(self, *, enabled_only: bool = False) -> list[Source]: ...

    @abstractmethod
    async def add(self, source: Source) -> Source: ...

    @abstractmethod
    async def update(self, source: Source) -> Source: ...

    @abstractmethod
    async def delete(self, source_id: UUID) -> None: ...

class CompanyRepository(ABC):
    @abstractmethod
    async def get(self, company_id: UUID) -> Optional[Company]: ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Company]: ...

    @abstractmethod
    async def list(self) -> list[Company]: ...

    @abstractmethod
    async def add(self, company: Company) -> Company: ...

    @abstractmethod
    async def update(self, company: Company) -> Company: ...

    @abstractmethod
    async def delete(self, company_id: UUID) -> None: ...

class SkillRepository(ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Skill]: ...

    @abstractmethod
    async def get_or_create(self, name: str) -> Skill: ...

class VacancyRepository(ABC):
    @abstractmethod
    async def get(self, vacancy_id: UUID) -> Optional[Vacancy]: ...

    @abstractmethod
    async def get_by_external_id(
            self, source_id: UUID, external_id: str
    ) -> Optional[Vacancy]: ...

    @abstractmethod
    async def list(
            self,
            *,
            status: Optional[str] = None,
            limit: int = 50,
            offset: int = 0,
    ) -> list[Vacancy]: ...

    @abstractmethod
    async def add(self, vacancy: Vacancy) -> Vacancy: ...

    @abstractmethod
    async def update(self, vacancy: Vacancy) -> Vacancy: ...

    @abstractmethod
    async def delete(self, vacancy_id: UUID) -> None: ...

class VacancyMetricRepository(ABC):
    @abstractmethod
    async def get_by_vacancy(self, vacancy_id: UUID) -> Optional[VacancyMetric]: ...

    @abstractmethod
    async def upsert(self, metric: VacancyMetric) -> VacancyMetric: ...

    @abstractmethod
    async def delete_by_vacancy(self, vacancy_id: UUID) -> None: ...

