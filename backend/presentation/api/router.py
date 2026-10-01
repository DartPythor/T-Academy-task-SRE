from __future__ import annotations

from fastapi import APIRouter

from backend.presentation.api.companies import router as companies_router
from backend.presentation.api.health import router as health_router
from backend.presentation.api.sources import router as sources_router
from backend.presentation.api.vacancies import router as vacancies_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(vacancies_router)
api_router.include_router(sources_router)
api_router.include_router(companies_router)

