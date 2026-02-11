"""Runbook model."""

from typing import Optional
from uuid import UUID
from sqlalchemy import String, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Runbook(BaseModel):
    """Runbook model."""

    __tablename__ = "runbooks"

    title: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    service_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("services.id"), nullable=True)
    environment_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("environments.id"), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
