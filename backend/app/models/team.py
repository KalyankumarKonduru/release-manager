"""Team model."""

from typing import Optional
from uuid import UUID
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Team(BaseModel):
    """Team model."""

    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slack_channel: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    member_count: Mapped[int] = mapped_column(default=0)
