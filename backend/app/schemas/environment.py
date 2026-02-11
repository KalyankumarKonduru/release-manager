"""Environment schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EnvironmentCreate(BaseModel):
    """Create environment request."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    environment_type: str = Field(pattern="^(dev|staging|production|test)$")
    config_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EnvironmentUpdate(BaseModel):
    """Update environment request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    environment_type: Optional[str] = Field(None, pattern="^(dev|staging|production|test)$")
    config_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EnvironmentResponse(BaseModel):
    """Environment response."""

    id: UUID
    name: str
    description: Optional[str]
    environment_type: str
    config_path: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
