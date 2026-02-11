"""User schemas."""

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Create user request."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    username: str = Field(min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Update user request."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """User response."""

    id: UUID
    email: str
    full_name: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    """Token payload."""

    sub: UUID
    exp: int
    iat: int
    type: str = "access"

    model_config = ConfigDict(from_attributes=True)
