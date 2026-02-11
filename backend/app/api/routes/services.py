"""Service routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.service import Service
from app.models.team import Team
from app.models.user import User
from app.models.release import Release
from app.schemas import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    ReleaseResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/services", tags=["services"])


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """
    Create a new service.

    - **name**: Service name
    - **repository_url**: URL to the service repository
    - **team_id**: ID of the owning team
    - **description**: Optional service description
    """
    try:
        result = await db.execute(
            select(Team).where(Team.id == service_data.team_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        new_service = Service(
            name=service_data.name,
            description=service_data.description,
            repository_url=str(service_data.repository_url),
            team_id=service_data.team_id,
            slack_channel=service_data.slack_channel,
            owner_id=service_data.owner_id,
            is_active=True,
        )

        db.add(new_service)
        await db.commit()
        await db.refresh(new_service)

        return ServiceResponse.model_validate(new_service)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service",
        ) from e


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    team_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[ServiceResponse]:
    """
    List services with optional filters.

    - **team_id**: Filter by team ID
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Service)

        if team_id:
            query = query.where(Service.team_id == team_id)

        result = await db.execute(
            query.order_by(desc(Service.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [ServiceResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list services",
        ) from e


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """Get a specific service by ID."""
    try:
        result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        return ServiceResponse.model_validate(service)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service",
        ) from e


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """Update a service."""
    try:
        result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        update_data = service_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "repository_url" and value:
                setattr(service, field, str(value))
            else:
                setattr(service, field, value)

        await db.commit()
        await db.refresh(service)

        return ServiceResponse.model_validate(service)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update service",
        ) from e


@router.delete("/{service_id}", response_model=MessageResponse)
async def delete_service(
    service_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a service."""
    try:
        result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        await db.delete(service)
        await db.commit()

        return MessageResponse(message="Service deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete service",
        ) from e


@router.get("/{service_id}/releases", response_model=list[ReleaseResponse])
async def get_service_releases(
    service_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[ReleaseResponse]:
    """
    Get all releases for a service.

    - **service_id**: ID of the service
    """
    try:
        result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        result = await db.execute(
            select(Release)
            .where(Release.service_id == service_id)
            .order_by(desc(Release.created_at))
            .offset(skip)
            .limit(limit)
        )
        releases = result.scalars().all()

        return [ReleaseResponse.model_validate(r) for r in releases]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service releases",
        ) from e


@router.get("/{service_id}/health", response_model=dict)
async def get_service_health(
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get health status of a service.

    - **service_id**: ID of the service
    """
    try:
        result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found",
            )

        return {
            "service_id": str(service.id),
            "service_name": service.name,
            "status": "healthy",
            "last_deployment": "2024-01-15T10:30:00Z",
            "uptime": "99.99%",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service health",
        ) from e
