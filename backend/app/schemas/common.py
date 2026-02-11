"""Common schemas for pagination and responses."""

from typing import Generic, TypeVar, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    database: str
    redis: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
