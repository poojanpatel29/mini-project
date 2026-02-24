from Core.database import Base
from datetime import datetime, date, UTC
from enum import Enum as eEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum as sEnum, Text, Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid


class InviteToken(Base):
    __tablename__ = "invite_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)

    team = relationship("Team",back_populates="invites")
