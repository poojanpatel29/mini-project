from Core.database import Base
from datetime import datetime, date, UTC
from enum import Enum as eEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum as sEnum, Text, Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(
    String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
    index=True
)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100),nullable=False)
    resource_id: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

    user = relationship("User",back_populates="activity_logs")
