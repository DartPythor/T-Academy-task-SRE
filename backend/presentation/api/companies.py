from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from backend.domain.entities import Company
from backend.infrastructure.db.repositories import SQLCompanyRepository
from backend.presentation.dependencies import SessionDep
from backend.presentation.schemas.company import CompanyCreateRequest, CompanyResponse

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    session: SessionDep,
) -> list[CompanyResponse]:
    repo = SQLCompanyRepository(session)
    companies = await repo.list()
    return [_company_to_response(c) for c in companies]

@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    body: CompanyCreateRequest,
    session: SessionDep,
) -> CompanyResponse:
    company = Company.create(name=body.name, website=body.website)
    company.description = body.description
    repo = SQLCompanyRepository(session)
    saved = await repo.add(company)
    await session.commit()
    return _company_to_response(saved)

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    session: SessionDep,
) -> CompanyResponse:
    repo = SQLCompanyRepository(session)
    company = await repo.get(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="company not found")
    return _company_to_response(company)

def _company_to_response(company: Company) -> CompanyResponse:
    return CompanyResponse(
        id=company.id,
        name=company.name,
        website=company.website,
        description=company.description,
        created_at=company.created_at,
        updated_at=company.updated_at,
    )
