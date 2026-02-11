"""Audit log schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """Audit log response."""

    id: UUID
    user_id: UUID
    action: str
    resource_type: str
    resource_id: UUID
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    """Audit log filter."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    user_id: Optional[UUID] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)

    model_config = ConfigDict(from_attributes=True)
