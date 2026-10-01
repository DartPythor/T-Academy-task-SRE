from __future__ import annotations

from uuid import UUID

from backend.application.dto.vacancy_dto import (
    CreateVacancyDTO,
    UpdateVacancyDTO,
)
from backend.application.ports.unit_of_work import UnitOfWork
from backend.application.services.metrics_calculator import MetricsCalculator
from backend.domain.entities import Company, Source, Vacancy
from backend.domain.enums import SourceType

class VacancyUseCases:
    def __init__(self, uow: UnitOfWork, calculator: MetricsCalculator) -> None:
        self._uow = uow
        self._calculator = calculator

    async def create(self, dto: CreateVacancyDTO) -> Vacancy:
        async with self._uow:
            source = await self._uow.sources.get(dto.source_id)
            if source is None:
                source = Source.create(
                    name=f"Manual ({str(dto.source_id)[:8]})",
                    type=SourceType.OTHER,
                    url=dto.url,
                )
                await self._uow.sources.add(source)
            source_id = source.id

            company_id = dto.company_id
            if company_id is None and dto.company_name:
                existing = await self._uow.companies.get_by_name(dto.company_name)
                if existing is None:
                    existing = await self._uow.companies.add(
                        Company.create(name=dto.company_name)
                    )
                company_id = existing.id

            vacancy = Vacancy.create(
                source_id=source_id,
                external_id=dto.external_id,
                title=dto.title,
                url=dto.url,
                description=dto.description,
                company_id=company_id,
                location=dto.location,
                employment_type=dto.employment_type,
                work_mode=dto.work_mode,
                published_at=dto.published_at,
                raw_data=dto.raw_data,
            )

            if dto.skill_names:
                for name in dto.skill_names:
                    skill = await self._uow.skills.get_or_create(name)
                    vacancy.add_skill(skill)

            metric = self._calculator.calculate(vacancy, dto.salary)
            vacancy.attach_metric(metric)

            await self._uow.vacancies.add(vacancy)
            await self._uow.metrics.upsert(metric)
            await self._uow.commit()
            return vacancy

    async def get(self, vacancy_id: UUID) -> Vacancy | None:
        async with self._uow:
            return await self._uow.vacancies.get(vacancy_id)

    async def list(
        self, *, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Vacancy]:
        async with self._uow:
            return await self._uow.vacancies.list(
                status=status, limit=limit, offset=offset
            )

    async def update(self, vacancy_id: UUID, dto: UpdateVacancyDTO) -> Vacancy:
        async with self._uow:
            vacancy = await self._uow.vacancies.get(vacancy_id)
            if vacancy is None:
                raise ValueError(f"vacancy {vacancy_id} not found")

            if dto.title is not None:
                vacancy.title = dto.title
            if dto.description is not None:
                vacancy.description = dto.description
            if dto.url is not None:
                vacancy.url = dto.url
            if dto.location is not None:
                vacancy.location = dto.location
            if dto.employment_type is not None:
                vacancy.employment_type = dto.employment_type
            if dto.work_mode is not None:
                vacancy.work_mode = dto.work_mode
            if dto.company_id is not None:
                vacancy.company_id = dto.company_id
            if dto.raw_data is not None:
                vacancy.raw_data = dto.raw_data
            if dto.status is not None:
                vacancy.status = dto.status

            if dto.skill_names is not None:
                vacancy.skills.clear()
                for name in dto.skill_names:
                    skill = await self._uow.skills.get_or_create(name)
                    vacancy.add_skill(skill)

            if dto.salary is not None:
                metric = self._calculator.calculate(vacancy, dto.salary)
                vacancy.attach_metric(metric)
                await self._uow.metrics.upsert(metric)

            await self._uow.vacancies.update(vacancy)
            await self._uow.commit()
            return vacancy

    async def delete(self, vacancy_id: UUID) -> None:
        async with self._uow:
            await self._uow.vacancies.delete(vacancy_id)
            await self._uow.commit()

class MetricUseCases:
    def __init__(self, uow: UnitOfWork, calculator: MetricsCalculator) -> None:
        self._uow = uow
        self._calculator = calculator

    async def recalculate(self, vacancy_id: UUID, salary: SalaryRange) -> Vacancy:
        async with self._uow:
            vacancy = await self._uow.vacancies.get(vacancy_id)
            if vacancy is None:
                raise ValueError(f"vacancy {vacancy_id} not found")

            new_metric = self._calculator.calculate(vacancy, salary)
            vacancy.attach_metric(new_metric)
            await self._uow.metrics.upsert(new_metric)
            await self._uow.commit()
            return vacancy

    async def get_metric(self, vacancy_id: UUID):
        async with self._uow:
            return await self._uow.metrics.get_by_vacancy(vacancy_id)

    async def delete_metric(self, vacancy_id: UUID) -> None:
        async with self._uow:
            await self._uow.metrics.delete_by_vacancy(vacancy_id)
            await self._uow.commit()

