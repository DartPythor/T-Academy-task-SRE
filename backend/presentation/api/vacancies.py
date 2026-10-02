from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from backend.application.dto.vacancy_dto import CreateVacancyDTO, UpdateVacancyDTO
from backend.domain.entities import Vacancy
from backend.domain.values import Money, SalaryRange
from backend.infrastructure.db.repositories import SQLCompanyRepository
from backend.presentation.dependencies import MetricUseCasesDep, SessionDep, VacancyUseCasesDep
from backend.presentation.schemas.common import PaginatedResponse
from backend.presentation.schemas.vacancy import (
    MetricResponse,
    RecalculateRequest,
    VacancyCreateRequest,
    VacancyResponse,
    VacancyUpdateRequest,
)

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

@router.get("", response_model=PaginatedResponse[VacancyResponse])
async def list_vacancies(
    use_cases: VacancyUseCasesDep,
    session: SessionDep,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[VacancyResponse]:
    vacancies = await use_cases.list(status=status_filter, limit=limit, offset=offset)
    company_repo = SQLCompanyRepository(session)
    items = [_vacancy_to_response(v, await _load_company_name(v, company_repo)) for v in vacancies]
    return PaginatedResponse(
        items=items,
        total=len(items),
        limit=limit,
        offset=offset,
    )

@router.post("", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    body: VacancyCreateRequest,
    use_cases: VacancyUseCasesDep,
    session: SessionDep,
) -> VacancyResponse:
    dto = CreateVacancyDTO(
        source_id=body.source_id,
        external_id=body.external_id,
        title=body.title,
        url=body.url,
        salary=_salary_to_domain(body.salary),
        description=body.description,
        company_id=body.company_id,
        company_name=body.company_name,
        location=body.location,
        employment_type=body.employment_type,
        work_mode=body.work_mode,
        published_at=body.published_at,
        raw_data=body.raw_data,
        skill_names=body.skill_names,
    )
    vacancy = await use_cases.create(dto)
    company_repo = SQLCompanyRepository(session)
    company_name = await _load_company_name(vacancy, company_repo)
    return _vacancy_to_response(vacancy, company_name)

@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: UUID,
    use_cases: VacancyUseCasesDep,
    session: SessionDep,
) -> VacancyResponse:
    vacancy = await use_cases.get(vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="vacancy not found")
    company_repo = SQLCompanyRepository(session)
    company_name = await _load_company_name(vacancy, company_repo)
    return _vacancy_to_response(vacancy, company_name)

@router.put("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: UUID,
    body: VacancyUpdateRequest,
    use_cases: VacancyUseCasesDep,
    session: SessionDep,
) -> VacancyResponse:
    dto = UpdateVacancyDTO(
        title=body.title,
        description=body.description,
        url=body.url,
        location=body.location,
        employment_type=body.employment_type,
        work_mode=body.work_mode,
        status=body.status,
        company_id=body.company_id,
        salary=_salary_to_domain(body.salary) if body.salary else None,
        raw_data=body.raw_data,
        skill_names=body.skill_names,
    )
    try:
        vacancy = await use_cases.update(vacancy_id, dto)
    except ValueError:
        raise HTTPException(status_code=404, detail="vacancy not found")
    company_repo = SQLCompanyRepository(session)
    company_name = await _load_company_name(vacancy, company_repo)
    return _vacancy_to_response(vacancy, company_name)

@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: UUID,
    use_cases: VacancyUseCasesDep,
) -> None:
    await use_cases.delete(vacancy_id)

@router.get("/{vacancy_id}/metrics", response_model=MetricResponse)
async def get_vacancy_metrics(
    vacancy_id: UUID,
    use_cases: MetricUseCasesDep,
) -> MetricResponse:
    metric = await use_cases.get_metric(vacancy_id)
    if metric is None:
        raise HTTPException(status_code=404, detail="metrics not found for vacancy")
    return _metric_to_response(metric)

@router.post("/{vacancy_id}/recalculate", response_model=VacancyResponse)
async def recalculate_metrics(
    vacancy_id: UUID,
    body: RecalculateRequest,
    use_cases: MetricUseCasesDep,
    session: SessionDep,
) -> VacancyResponse:
    salary = _salary_to_domain(body.salary)
    try:
        vacancy = await use_cases.recalculate(vacancy_id, salary)
    except ValueError:
        raise HTTPException(status_code=404, detail="vacancy not found")
    company_repo = SQLCompanyRepository(session)
    company_name = await _load_company_name(vacancy, company_repo)
    return _vacancy_to_response(vacancy, company_name)

@router.delete("/{vacancy_id}/metrics", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy_metrics(
    vacancy_id: UUID,
    use_cases: MetricUseCasesDep,
) -> None:
    await use_cases.delete_metric(vacancy_id)

async def _load_company_name(v: Vacancy, repo: SQLCompanyRepository) -> str | None:
    if v.company_id is None:
        return None
    company = await repo.get(v.company_id)
    return company.name if company else None

def _vacancy_to_response(v: Vacancy, company_name: str | None = None) -> VacancyResponse:
    metric: MetricResponse | None = None
    if v.metric is not None:
        metric = _metric_to_response(v.metric)

    return VacancyResponse(
        id=v.id,
        source_id=v.source_id,
        external_id=v.external_id,
        title=v.title,
        url=v.url,
        description=v.description,
        company_id=v.company_id,
        company_name=company_name,
        location=v.location,
        employment_type=v.employment_type.value if v.employment_type else None,
        work_mode=v.work_mode.value if v.work_mode else None,
        published_at=v.published_at,
        status=v.status,
        skills=[{"id": s.id, "name": s.name} for s in v.skills],
        metric=metric,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )

def _metric_to_response(m) -> MetricResponse:
    return MetricResponse(
        salary_min=_money_to_schema(m.salary.min_amount),
        salary_max=_money_to_schema(m.salary.max_amount),
        scam_score=m.scam_score.value,
        apply_score=m.apply_score.value,
        confidence=m.confidence.value,
        details=m.details,
        calculated_at=m.calculated_at,
    )

def _money_to_schema(money: Money | None):
    if money is None:
        return None
    return {"amount": money.amount, "currency": money.currency}

def _salary_to_domain(s: SalaryRange) -> SalaryRange:
    min_money = Money(amount=s.min_amount.amount, currency=s.min_amount.currency) if s.min_amount else None
    max_money = Money(amount=s.max_amount.amount, currency=s.max_amount.currency) if s.max_amount else None
    return SalaryRange(min_amount=min_money, max_amount=max_money, gross=s.gross)

