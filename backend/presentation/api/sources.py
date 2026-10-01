from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from backend.domain.entities import Source
from backend.infrastructure.db.repositories import SQLSourceRepository
from backend.presentation.dependencies import SessionDep
from backend.presentation.schemas.source import (
    SourceCreateRequest,
    SourceResponse,
    SourceUpdateRequest,
)

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get("", response_model=list[SourceResponse])
async def list_sources(
    session: SessionDep,
    enabled_only: bool = False,
) -> list[SourceResponse]:
    repo = SQLSourceRepository(session)
    sources = await repo.list(enabled_only=enabled_only)
    return [_source_to_response(s) for s in sources]

@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    body: SourceCreateRequest,
    session: SessionDep,
) -> SourceResponse:
    source = Source.create(name=body.name, type=body.type, url=body.url)
    repo = SQLSourceRepository(session)
    saved = await repo.add(source)
    await session.commit()
    return _source_to_response(saved)

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: UUID,
    session: SessionDep,
) -> SourceResponse:
    repo = SQLSourceRepository(session)
    source = await repo.get(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")
    return _source_to_response(source)

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: UUID,
    body: SourceUpdateRequest,
    session: SessionDep,
) -> SourceResponse:
    repo = SQLSourceRepository(session)
    source = await repo.get(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="source not found")

    if body.name is not None:
        source.name = body.name
    if body.type is not None:
        source.type = body.type
    if body.url is not None:
        source.url = body.url
    if body.enabled is not None:
        source.enabled = body.enabled

    updated = await repo.update(source)
    await session.commit()
    return _source_to_response(updated)

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID,
    session: SessionDep,
) -> None:
    repo = SQLSourceRepository(session)
    await repo.delete(source_id)
    await session.commit()

def _source_to_response(source: Source) -> SourceResponse:
    return SourceResponse(
        id=source.id,
        name=source.name,
        type=source.type,
        url=source.url,
        enabled=source.enabled,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )
