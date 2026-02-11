"""Release model."""

from typing import Optional
from uuid import UUID
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Release(BaseModel):
    """Release model."""

    __tablename__ = "releases"

    service_id: Mapped[UUID] = mapped_column(ForeignKey("services.id"), index=True)
    version: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    release_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    git_commit: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
