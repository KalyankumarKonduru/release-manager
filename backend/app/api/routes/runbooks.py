"""Runbook routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.runbook import Runbook
from app.models.user import User
from app.schemas import (
    RunbookCreate,
    RunbookUpdate,
    RunbookResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/runbooks", tags=["runbooks"])


@router.post("", response_model=RunbookResponse, status_code=status.HTTP_201_CREATED)
async def create_runbook(
    runbook_data: RunbookCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> RunbookResponse:
    """
    Create a new runbook.

    - **title**: Runbook title
    - **content**: Runbook content (markdown)
    - **service_id**: Optional service ID
    - **environment_id**: Optional environment ID
    - **tags**: Optional list of tags
    """
    try:
        new_runbook = Runbook(
            title=runbook_data.title,
            content=runbook_data.content,
            service_id=runbook_data.service_id,
            environment_id=runbook_data.environment_id,
            tags=runbook_data.tags or [],
            created_by=current_user.id,
            is_active=True,
        )

        db.add(new_runbook)
        await db.commit()
        await db.refresh(new_runbook)

        return RunbookResponse.model_validate(new_runbook)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create runbook",
        ) from e


@router.get("", response_model=list[RunbookResponse])
async def list_runbooks(
    service_id: Optional[UUID] = Query(None),
    environment_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[RunbookResponse]:
    """
    List runbooks with optional filters.

    - **service_id**: Filter by service ID
    - **environment_id**: Filter by environment ID
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Runbook).where(Runbook.is_active == True)

        if service_id:
            query = query.where(Runbook.service_id == service_id)
        if environment_id:
            query = query.where(Runbook.environment_id == environment_id)

        result = await db.execute(
            query.order_by(desc(Runbook.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [RunbookResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list runbooks",
        ) from e


@router.get("/{runbook_id}", response_model=RunbookResponse)
async def get_runbook(
    runbook_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RunbookResponse:
    """Get a specific runbook by ID."""
    try:
        result = await db.execute(
            select(Runbook).where(Runbook.id == runbook_id)
        )
        runbook = result.scalar_one_or_none()

        if not runbook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Runbook not found",
            )

        return RunbookResponse.model_validate(runbook)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get runbook",
        ) from e


@router.put("/{runbook_id}", response_model=RunbookResponse)
async def update_runbook(
    runbook_id: UUID,
    runbook_data: RunbookUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> RunbookResponse:
    """Update a runbook."""
    try:
        result = await db.execute(
            select(Runbook).where(Runbook.id == runbook_id)
        )
        runbook = result.scalar_one_or_none()

        if not runbook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Runbook not found",
            )

        update_data = runbook_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(runbook, field, value)

        await db.commit()
        await db.refresh(runbook)

        return RunbookResponse.model_validate(runbook)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update runbook",
        ) from e


@router.delete("/{runbook_id}", response_model=MessageResponse)
async def delete_runbook(
    runbook_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a runbook."""
    try:
        result = await db.execute(
            select(Runbook).where(Runbook.id == runbook_id)
        )
        runbook = result.scalar_one_or_none()

        if not runbook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Runbook not found",
            )

        runbook.is_active = False
        await db.commit()

        return MessageResponse(message="Runbook deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete runbook",
        ) from e


@router.get("/search/full-text", response_model=list[RunbookResponse])
async def search_runbooks(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[RunbookResponse]:
    """
    Search runbooks using full-text search.

    - **q**: Search query (searches title and content)
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        search_term = f"%{q}%"
        query = select(Runbook).where(
            or_(
                Runbook.title.ilike(search_term),
                Runbook.content.ilike(search_term),
            )
        )

        result = await db.execute(
            query.where(Runbook.is_active == True)
            .order_by(desc(Runbook.created_at))
            .offset(skip)
            .limit(limit)
        )
        items = result.scalars().all()

        return [RunbookResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search runbooks",
        ) from e
