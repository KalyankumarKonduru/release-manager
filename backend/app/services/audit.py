"""Audit logging service for tracking system actions and changes."""

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    """Service for managing audit logs."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: Optional[UUID],
        action: str,
        resource_type: str,
        resource_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an action to the audit log.

        Args:
            db: Database session
            user_id: ID of the user performing the action
            action: The action being performed (e.g., 'create', 'update', 'delete')
            resource_type: The type of resource being acted upon
            resource_id: The ID of the resource
            metadata: Additional metadata about the action
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            The created AuditLog record
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit_log)
        await db.flush()
        return audit_log

    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[AuditLog], int]:
        """
        Retrieve audit logs with optional filtering and pagination.

        Args:
            db: Database session
            filters: Dictionary of filter criteria:
                - user_id: Filter by user ID
                - action: Filter by action type
                - resource_type: Filter by resource type
                - resource_id: Filter by resource ID
                - start_date: Filter logs after this datetime
                - end_date: Filter logs before this datetime
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            Tuple of (list of AuditLog records, total count)
        """
        filters = filters or {}
        query = select(AuditLog)

        # Apply filters
        conditions = []

        if "user_id" in filters and filters["user_id"]:
            conditions.append(AuditLog.user_id == filters["user_id"])

        if "action" in filters and filters["action"]:
            conditions.append(AuditLog.action == filters["action"])

        if "resource_type" in filters and filters["resource_type"]:
            conditions.append(AuditLog.resource_type == filters["resource_type"])

        if "resource_id" in filters and filters["resource_id"]:
            conditions.append(AuditLog.resource_id == filters["resource_id"])

        if "start_date" in filters and filters["start_date"]:
            conditions.append(AuditLog.created_at >= filters["start_date"])

        if "end_date" in filters and filters["end_date"]:
            conditions.append(AuditLog.created_at <= filters["end_date"])

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_result = await db.execute(select(select(AuditLog).where(and_(*conditions) if conditions else True).correlate(None).scalar_subquery()))
        total = count_result.scalar() or 0

        # Apply ordering and pagination
        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)

        result = await db.execute(query)
        logs = result.scalars().all()

        # Get actual count
        count_query = select(AuditLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(select(select(count_query).correlate(None).scalar_subquery()))
        total = count_result.scalar() or 0

        return logs, total

    @staticmethod
    async def export_audit_logs_csv(
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Export audit logs as CSV.

        Args:
            db: Database session
            filters: Dictionary of filter criteria (same as get_audit_logs)

        Returns:
            CSV string with audit log data
        """
        filters = filters or {}
        query = select(AuditLog)

        # Apply filters
        conditions = []

        if "user_id" in filters and filters["user_id"]:
            conditions.append(AuditLog.user_id == filters["user_id"])

        if "action" in filters and filters["action"]:
            conditions.append(AuditLog.action == filters["action"])

        if "resource_type" in filters and filters["resource_type"]:
            conditions.append(AuditLog.resource_type == filters["resource_type"])

        if "resource_id" in filters and filters["resource_id"]:
            conditions.append(AuditLog.resource_id == filters["resource_id"])

        if "start_date" in filters and filters["start_date"]:
            conditions.append(AuditLog.created_at >= filters["start_date"])

        if "end_date" in filters and filters["end_date"]:
            conditions.append(AuditLog.created_at <= filters["end_date"])

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(AuditLog.created_at))

        result = await db.execute(query)
        logs = result.scalars().all()

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "ID",
            "User ID",
            "Action",
            "Resource Type",
            "Resource ID",
            "Details",
            "IP Address",
            "User Agent",
            "Created At",
        ])

        # Write data rows
        for log in logs:
            writer.writerow([
                str(log.id),
                str(log.user_id) if log.user_id else "",
                log.action,
                log.resource_type,
                str(log.resource_id),
                json.dumps(log.details) if log.details else "",
                log.ip_address or "",
                log.user_agent or "",
                log.created_at.isoformat() if log.created_at else "",
            ])

        return output.getvalue()
