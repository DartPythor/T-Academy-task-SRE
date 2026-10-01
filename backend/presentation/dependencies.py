from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.services.apply_advisor import ApplyAdvisor
from backend.application.services.metrics_calculator import MetricsCalculator
from backend.application.services.scam_detector import ScamDetector
from backend.application.use_cases.vacancy_use_cases import MetricUseCases, VacancyUseCases
from backend.infrastructure.db.repositories import (
    SQLCompanyRepository,
    SQLSkillRepository,
    SQLSourceRepository,
    SQLVacancyMetricRepository,
    SQLVacancyRepository,
)
from backend.infrastructure.db.session import get_session
from backend.infrastructure.db.unit_of_work import SQLUnitOfWork

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def build_calculator() -> MetricsCalculator:
    return MetricsCalculator(
        scam_detector=ScamDetector(),
        apply_advisor=ApplyAdvisor(),
    )

def build_uow(session: AsyncSession) -> SQLUnitOfWork:
    return SQLUnitOfWork(
        session=session,
        source_repo=SQLSourceRepository(session),
        company_repo=SQLCompanyRepository(session),
        skill_repo=SQLSkillRepository(session),
        vacancy_repo=SQLVacancyRepository(session),
        metric_repo=SQLVacancyMetricRepository(session),
    )

async def get_vacancy_use_cases(
    session: SessionDep,
) -> VacancyUseCases:
    return VacancyUseCases(uow=build_uow(session), calculator=build_calculator())

async def get_metric_use_cases(
    session: SessionDep,
) -> MetricUseCases:
    return MetricUseCases(uow=build_uow(session), calculator=build_calculator())

VacancyUseCasesDep = Annotated[VacancyUseCases, Depends(get_vacancy_use_cases)]
MetricUseCasesDep = Annotated[MetricUseCases, Depends(get_metric_use_cases)]
