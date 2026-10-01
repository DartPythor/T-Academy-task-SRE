from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type

from backend.application.ports.repositories import (
    CompanyRepository,
    SkillRepository,
    SourceRepository,
    VacancyMetricRepository,
    VacancyRepository,
)

class UnitOfWork(ABC):
    """Транзакционная граница для группы операций."""

    sources: SourceRepository
    companies: CompanyRepository
    skills: SkillRepository
    vacancies: VacancyRepository
    metrics: VacancyMetricRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork": ...

    @abstractmethod
    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

