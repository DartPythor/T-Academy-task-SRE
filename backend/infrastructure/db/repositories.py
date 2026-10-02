from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.application.ports.repositories import (
    CompanyRepository,
    SkillRepository,
    SourceRepository,
    VacancyMetricRepository,
    VacancyRepository,
)
from backend.domain.entities import Company, Skill, Source, Vacancy, VacancyMetric
from backend.infrastructure.db.mappers import (
    company_to_domain,
    company_to_orm,
    metric_to_domain,
    metric_to_orm,
    skill_to_domain,
    skill_to_orm,
    source_to_domain,
    source_to_orm,
    vacancy_list_to_domain,
    vacancy_to_domain,
    vacancy_to_orm,
)
from backend.infrastructure.db.models import (
    CompanyORM,
    SkillORM,
    SourceORM,
    VacancyMetricORM,
    VacancyORM,
)

class SQLSourceRepository(SourceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, source_id: UUID) -> Optional[Source]:
        orm = await self._session.get(SourceORM, source_id)
        return source_to_domain(orm) if orm else None

    async def list(self, *, enabled_only: bool = False) -> list[Source]:
        stmt = select(SourceORM)
        if enabled_only:
            stmt = stmt.where(SourceORM.enabled.is_(True))
        result = await self._session.execute(stmt)
        return [source_to_domain(row) for row in result.scalars()]

    async def add(self, source: Source) -> Source:
        orm = source_to_orm(source)
        self._session.add(orm)
        await self._session.flush()
        return source

    async def update(self, source: Source) -> Source:
        orm = await self._session.get(SourceORM, source.id)
        if orm is None:
            raise ValueError(f"source {source.id} not found")
        source_to_orm(source, orm)
        await self._session.flush()
        return source

    async def delete(self, source_id: UUID) -> None:
        orm = await self._session.get(SourceORM, source_id)
        if orm:
            await self._session.delete(orm)
            await self._session.flush()

class SQLCompanyRepository(CompanyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, company_id: UUID) -> Optional[Company]:
        orm = await self._session.get(CompanyORM, company_id)
        return company_to_domain(orm) if orm else None

    async def get_by_name(self, name: str) -> Optional[Company]:
        stmt = select(CompanyORM).where(CompanyORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return company_to_domain(orm) if orm else None

    async def list(self) -> list[Company]:
        result = await self._session.execute(select(CompanyORM))
        return [company_to_domain(row) for row in result.scalars()]

    async def add(self, company: Company) -> Company:
        orm = company_to_orm(company)
        self._session.add(orm)
        await self._session.flush()
        return company

    async def update(self, company: Company) -> Company:
        orm = await self._session.get(CompanyORM, company.id)
        if orm is None:
            raise ValueError(f"company {company.id} not found")
        company_to_orm(company, orm)
        await self._session.flush()
        return company

    async def delete(self, company_id: UUID) -> None:
        orm = await self._session.get(CompanyORM, company_id)
        if orm:
            await self._session.delete(orm)
            await self._session.flush()

class SQLSkillRepository(SkillRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_name(self, name: str) -> Optional[Skill]:
        stmt = select(SkillORM).where(SkillORM.name == name.strip().lower())
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return skill_to_domain(orm) if orm else None

    async def get_or_create(self, name: str) -> Skill:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        skill = Skill.create(name)
        orm = skill_to_orm(skill)
        self._session.add(orm)
        await self._session.flush()
        return skill

class SQLVacancyRepository(VacancyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, vacancy_id: UUID) -> Optional[Vacancy]:
        stmt = (
            select(VacancyORM)
            .options(selectinload(VacancyORM.metric))
            .where(VacancyORM.id == vacancy_id)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return vacancy_to_domain(orm) if orm else None

    async def get_by_external_id(
        self, source_id: UUID, external_id: str
    ) -> Optional[Vacancy]:
        stmt = (
            select(VacancyORM)
            .options(selectinload(VacancyORM.metric))
            .where(
                VacancyORM.source_id == source_id,
                VacancyORM.external_id == external_id,
            )
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return vacancy_to_domain(orm) if orm else None

    async def list(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Vacancy]:
        stmt = select(VacancyORM).options(
            selectinload(VacancyORM.metric),
        ).order_by(VacancyORM.created_at.desc())
        if status is not None:
            stmt = stmt.where(VacancyORM.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return vacancy_list_to_domain(result.scalars().all())

    async def add(self, vacancy: Vacancy) -> Vacancy:
        orm = vacancy_to_orm(vacancy)
        self._session.add(orm)
        await self._session.flush()

        if vacancy.skills:
            from backend.infrastructure.db.models import VacancySkillORM
            for skill in vacancy.skills:
                skill_orm = await self._session.get(SkillORM, skill.id)
                if skill_orm:
                    self._session.add(VacancySkillORM(vacancy_id=orm.id, skill_id=skill.id))
            await self._session.flush()
        return vacancy

    async def update(self, vacancy: Vacancy) -> Vacancy:
        orm = await self._session.get(VacancyORM, vacancy.id)
        if orm is None:
            raise ValueError(f"vacancy {vacancy.id} not found")
        vacancy_to_orm(vacancy, orm)

        from backend.infrastructure.db.models import VacancySkillORM
        from sqlalchemy import delete
        await self._session.execute(
            delete(VacancySkillORM).where(VacancySkillORM.vacancy_id == vacancy.id)
        )
        for skill in vacancy.skills:
            skill_orm = await self._session.get(SkillORM, skill.id)
            if skill_orm:
                self._session.add(VacancySkillORM(vacancy_id=orm.id, skill_id=skill.id))

        await self._session.flush()
        return vacancy

    async def delete(self, vacancy_id: UUID) -> None:
        orm = await self._session.get(VacancyORM, vacancy_id)
        if orm:
            await self._session.delete(orm)
            await self._session.flush()

class SQLVacancyMetricRepository(VacancyMetricRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_vacancy(self, vacancy_id: UUID) -> Optional[VacancyMetric]:
        stmt = select(VacancyMetricORM).where(
            VacancyMetricORM.vacancy_id == vacancy_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return metric_to_domain(orm) if orm else None

    async def upsert(self, metric: VacancyMetric) -> VacancyMetric:
        stmt = select(VacancyMetricORM).where(
            VacancyMetricORM.vacancy_id == metric.vacancy_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        metric_to_orm(metric, orm)
        if orm is None:
            self._session.add(metric_to_orm(metric))
        await self._session.flush()
        return metric

    async def delete_by_vacancy(self, vacancy_id: UUID) -> None:
        stmt = select(VacancyMetricORM).where(
            VacancyMetricORM.vacancy_id == vacancy_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm:
            await self._session.delete(orm)
            await self._session.flush()
