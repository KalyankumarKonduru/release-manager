"""Rollback schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RollbackCreate(BaseModel):
    """Create rollback request."""

    deployment_id: UUID
    target_release_id: UUID
    reason: str = Field(min_length=10)
    initiated_by: UUID

    model_config = ConfigDict(from_attributes=True)


class RollbackResponse(BaseModel):
    """Rollback response."""

    id: UUID
    deployment_id: UUID
    target_release_id: UUID
    reason: str
    status: str
    initiated_by: UUID
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
