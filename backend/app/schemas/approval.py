"""Approval schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ApprovalCreate(BaseModel):
    """Create approval request."""

    deployment_id: UUID
    required_approvers: int = Field(ge=1)

    model_config = ConfigDict(from_attributes=True)


class ApprovalUpdate(BaseModel):
    """Update approval request."""

    status: str = Field(pattern="^(approved|rejected)$")
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalResponse(BaseModel):
    """Approval response."""

    id: UUID
    deployment_id: UUID
    approver_id: UUID
    status: str
    notes: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
