from Core.database import Base
from datetime import datetime, date, UTC
from enum import Enum as eEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum as sEnum, Text, Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(nullable=False)
    resource_id: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

    user = relationship("User",back_populates="activity_logs")
