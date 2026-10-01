from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.ports.unit_of_work import UnitOfWork
from backend.infrastructure.db.repositories import (
    SQLCompanyRepository,
    SQLSkillRepository,
    SQLSourceRepository,
    SQLVacancyMetricRepository,
    SQLVacancyRepository,
)

class SQLUnitOfWork(UnitOfWork):
    """Реализация UnitOfWork на SQLAlchemy AsyncSession."""

    def __init__(
        self,
        session: AsyncSession,
        source_repo: SQLSourceRepository,
        company_repo: SQLCompanyRepository,
        skill_repo: SQLSkillRepository,
        vacancy_repo: SQLVacancyRepository,
        metric_repo: SQLVacancyMetricRepository,
    ) -> None:
        self._session = session
        self.sources = source_repo
        self.companies = company_repo
        self.skills = skill_repo
        self.vacancies = vacancy_repo
        self.metrics = metric_repo

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if exc_type is not None:
            await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
