from __future__ import annotations

from typing import Optional

from backend.domain.entities import (
    Company,
    Skill,
    Source,
    Vacancy,
    VacancyMetric,
)
from backend.domain.enums import (
    Currency,
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
from backend.infrastructure.db.models import (
    CompanyORM,
    SkillORM,
    SourceORM,
    VacancyMetricORM,
    VacancyORM,
)

def source_to_domain(orm: SourceORM) -> Source:
    return Source(
        id=orm.id,
        name=orm.name,
        type=SourceType(orm.type),
        url=orm.url,
        enabled=orm.enabled,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )

def source_to_orm(domain: Source, orm: Optional[SourceORM] = None) -> SourceORM:
    orm = orm or SourceORM()
    orm.id = domain.id
    orm.name = domain.name
    orm.type = domain.type.value
    orm.url = domain.url
    orm.enabled = domain.enabled
    orm.created_at = domain.created_at
    orm.updated_at = domain.updated_at
    return orm

def company_to_domain(orm: CompanyORM) -> Company:
    return Company(
        id=orm.id,
        name=orm.name,
        website=orm.website,
        description=orm.description,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )

def company_to_orm(domain: Company, orm: Optional[CompanyORM] = None) -> CompanyORM:
    orm = orm or CompanyORM()
    orm.id = domain.id
    orm.name = domain.name
    orm.website = domain.website
    orm.description = domain.description
    orm.created_at = domain.created_at
    orm.updated_at = domain.updated_at
    return orm

def skill_to_domain(orm: SkillORM) -> Skill:
    return Skill(id=orm.id, name=orm.name)

def skill_to_orm(domain: Skill, orm: Optional[SkillORM] = None) -> SkillORM:
    orm = orm or SkillORM()
    orm.id = domain.id
    orm.name = domain.name
    return orm

def _salary_to_orm(salary: SalaryRange) -> dict:
    """Раскладывает VO SalaryRange в набор колонок."""
    min_amount = salary.min_amount
    max_amount = salary.max_amount
    currency = (
        (min_amount or max_amount).currency
        if (min_amount or max_amount) is not None
        else None
    )
    return {
        "salary_min": min_amount.amount if min_amount else None,
        "salary_max": max_amount.amount if max_amount else None,
        "salary_currency": currency.value if currency else None,
        "salary_gross": salary.gross,
    }

def _salary_from_orm(orm: VacancyMetricORM) -> SalaryRange:
    """Собирает SalaryRange из колонок. Учитывает частично заданные границы."""
    currency = Currency(orm.salary_currency) if orm.salary_currency else None

    min_money: Optional[Money] = None
    max_money: Optional[Money] = None

    if orm.salary_min is not None and currency is not None:
        min_money = Money(amount=orm.salary_min, currency=currency)
    if orm.salary_max is not None and currency is not None:
        max_money = Money(amount=orm.salary_max, currency=currency)

    return SalaryRange(
        min_amount=min_money,
        max_amount=max_money,
        gross=orm.salary_gross,
    )

def metric_to_domain(orm: VacancyMetricORM) -> VacancyMetric:
    return VacancyMetric(
        id=orm.id,
        vacancy_id=orm.vacancy_id,
        salary=_salary_from_orm(orm),
        scam_score=ScamScore(orm.scam_score),
        apply_score=ApplyScore(orm.apply_score),
        confidence=Confidence(float(orm.confidence)),
        details=dict(orm.details or {}),
        calculated_at=orm.calculated_at,
    )

def metric_to_orm(
    domain: VacancyMetric, orm: Optional[VacancyMetricORM] = None
) -> VacancyMetricORM:
    orm = orm or VacancyMetricORM()
    orm.id = domain.id
    orm.vacancy_id = domain.vacancy_id
    for column, value in _salary_to_orm(domain.salary).items():
        setattr(orm, column, value)
    orm.scam_score = domain.scam_score.value
    orm.apply_score = domain.apply_score.value
    from decimal import Decimal
    orm.confidence = Decimal(f"{domain.confidence.value:.2f}")
    orm.details = dict(domain.details or {})
    orm.calculated_at = domain.calculated_at
    return orm

def vacancy_to_domain(orm: VacancyORM) -> Vacancy:
    return Vacancy(
        id=orm.id,
        source_id=orm.source_id,
        external_id=orm.external_id,
        title=orm.title,
        url=orm.url,
        description=orm.description,
        company_id=orm.company_id,
        location=orm.location,
        employment_type=(
            EmploymentType(orm.employment_type) if orm.employment_type else None
        ),
        work_mode=WorkMode(orm.work_mode) if orm.work_mode else None,
        published_at=orm.published_at,
        status=VacancyStatus(orm.status),
        raw_data=dict(orm.raw_data or {}),
        skills=[skill_to_domain(s) for s in orm.skills],
        metric=metric_to_domain(orm.metric) if orm.metric else None,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )

def vacancy_to_orm(domain: Vacancy, orm: Optional[VacancyORM] = None) -> VacancyORM:
    """Обновляет/создаёт ORM-объект Vacancy без связей skills/metric.

    Связи metric и skills обновляются отдельно через relationship,
    потому что они — отдельные сущности (metric) и M2M (skills).
    """
    orm = orm or VacancyORM()
    orm.id = domain.id
    orm.source_id = domain.source_id
    orm.company_id = domain.company_id
    orm.external_id = domain.external_id
    orm.title = domain.title
    orm.description = domain.description
    orm.url = domain.url
    orm.location = domain.location
    orm.employment_type = (
        domain.employment_type.value if domain.employment_type else None
    )
    orm.work_mode = domain.work_mode.value if domain.work_mode else None
    orm.published_at = domain.published_at
    orm.status = domain.status.value
    orm.raw_data = dict(domain.raw_data or {})
    orm.created_at = domain.created_at
    orm.updated_at = domain.updated_at
    return orm

def vacancy_list_to_domain(orms: list[VacancyORM]) -> list[Vacancy]:
    return [vacancy_to_domain(o) for o in orms]

def sources_list_to_domain(orms: list[SourceORM]) -> list[Source]:
    return [source_to_domain(o) for o in orms]

def companies_list_to_domain(orms: list[CompanyORM]) -> list[Company]:
    return [company_to_domain(o) for o in orms]

