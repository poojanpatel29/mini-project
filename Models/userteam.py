from core.database import Base
from datetime import datetime, date, UTC
from enum import Enum as eEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum as sEnum, Text, Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid


class UserTeam(Base):
    __tablename__ = "user_teams"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
