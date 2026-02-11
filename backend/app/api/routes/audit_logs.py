"""Audit log routes."""

from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas import (
    AuditLogResponse,
    AuditLogFilter,
)

router = APIRouter(prefix="/api/audit-logs", tags=["audit_logs"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    user_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    """
    List audit logs with optional filters.

    - **start_date**: Filter logs from this date
    - **end_date**: Filter logs until this date
    - **action**: Filter by action type (create, update, delete, deploy, etc.)
    - **resource_type**: Filter by resource type
    - **user_id**: Filter by user ID
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    """
    try:
        query = select(AuditLog)

        conditions = []
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)

        if conditions:
            query = query.where(and_(*conditions))

        result = await db.execute(
            query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return [AuditLogResponse.model_validate(item) for item in items]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list audit logs",
        ) from e


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:
    """Get a specific audit log by ID."""
    try:
        result = await db.execute(
            select(AuditLog).where(AuditLog.id == log_id)
        )
        log = result.scalar_one_or_none()

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit log not found",
            )

        return AuditLogResponse.model_validate(log)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get audit log",
        ) from e


@router.get("/export/csv")
async def export_audit_logs_csv(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    user_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Export audit logs as CSV.

    - **start_date**: Filter logs from this date
    - **end_date**: Filter logs until this date
    - **action**: Filter by action type
    - **resource_type**: Filter by resource type
    - **user_id**: Filter by user ID
    """
    try:
        query = select(AuditLog)

        conditions = []
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)

        if conditions:
            query = query.where(and_(*conditions))

        result = await db.execute(
            query.order_by(desc(AuditLog.created_at)).limit(10000)
        )
        logs = result.scalars().all()

        csv_output = StringIO()
        csv_output.write("ID,User ID,Action,Resource Type,Resource ID,Details,IP Address,User Agent,Created At\n")

        for log in logs:
            details_str = str(log.details).replace('"', '""') if log.details else ""
            csv_output.write(
                f"{log.id},{log.user_id},{log.action},{log.resource_type},"
                f"{log.resource_id},\"{details_str}\",{log.ip_address},"
                f"{log.user_agent},{log.created_at}\n"
            )

        csv_output.seek(0)
        return StreamingResponse(
            iter([csv_output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export audit logs",
        ) from e
