"""Approval routes."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.approval import Approval
from app.models.deployment import Deployment
from app.models.user import User
from app.schemas import (
    ApprovalCreate,
    ApprovalUpdate,
    ApprovalResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.post("", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_approval(
    approval_data: ApprovalCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """
    Create a new approval request.

    - **deployment_id**: ID of the deployment requiring approval
    - **required_approvers**: Number of approvers required
    """
    try:
        result = await db.execute(
            select(Deployment).where(Deployment.id == approval_data.deployment_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment not found",
            )

        new_approval = Approval(
            deployment_id=approval_data.deployment_id,
            approver_id=current_user.id,
            status="pending",
        )

        db.add(new_approval)
        await db.commit()
        await db.refresh(new_approval)

        return ApprovalResponse.model_validate(new_approval)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create approval",
        ) from e


@router.get("", response_model=list[ApprovalResponse])
async def list_approvals(
    status: Optional[str] = Query(None),
    deployment_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[ApprovalResponse]:
    """
    List approvals with optional filters.

    - **status**: Filter by status (pending, approved, rejected)
    - **deployment_id**: Filter by deployment ID
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(Approval)

        if status:
            query = query.where(Approval.status == status)
        if deployment_id:
            query = query.where(Approval.deployment_id == deployment_id)

        result = await db.execute(
            query.order_by(desc(Approval.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [ApprovalResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list approvals",
        ) from e


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """Get a specific approval by ID."""
    try:
        result = await db.execute(
            select(Approval).where(Approval.id == approval_id)
        )
        approval = result.scalar_one_or_none()

        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found",
            )

        return ApprovalResponse.model_validate(approval)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get approval",
        ) from e


@router.put("/{approval_id}", response_model=ApprovalResponse)
async def update_approval(
    approval_id: UUID,
    approval_data: ApprovalUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """
    Update an approval (approve or reject).

    - **approval_id**: ID of the approval to update
    - **status**: Status update (approved or rejected)
    - **notes**: Optional notes for rejection
    """
    try:
        result = await db.execute(
            select(Approval).where(Approval.id == approval_id)
        )
        approval = result.scalar_one_or_none()

        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found",
            )

        update_data = approval_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status":
                setattr(approval, field, value)
                if value == "approved":
                    from datetime import datetime
                    setattr(approval, "approved_at", datetime.utcnow())
            else:
                setattr(approval, field, value)

        await db.commit()
        await db.refresh(approval)

        return ApprovalResponse.model_validate(approval)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update approval",
        ) from e


@router.delete("/{approval_id}", response_model=MessageResponse)
async def delete_approval(
    approval_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete an approval."""
    try:
        result = await db.execute(
            select(Approval).where(Approval.id == approval_id)
        )
        approval = result.scalar_one_or_none()

        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found",
            )

        await db.delete(approval)
        await db.commit()

        return MessageResponse(message="Approval deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete approval",
        ) from e
