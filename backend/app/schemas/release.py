"""Release schemas."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from .common import PaginatedResponse


class ReleaseCreate(BaseModel):
    """Create release request."""

    service_id: UUID
    version: str = Field(min_length=1, max_length=50)
    release_notes: Optional[str] = None
    git_commit: Optional[str] = None
    created_by: UUID

    model_config = ConfigDict(from_attributes=True)


class ReleaseUpdate(BaseModel):
    """Update release request."""

    version: Optional[str] = Field(None, min_length=1, max_length=50)
    release_notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|deployed|failed)$")

    model_config = ConfigDict(from_attributes=True)


class ReleaseResponse(BaseModel):
    """Release response."""

    id: UUID
    service_id: UUID
    version: str
    status: str
    release_notes: Optional[str]
    git_commit: Optional[str]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReleaseListResponse(PaginatedResponse[ReleaseResponse]):
    """Paginated release list response."""

    pass
