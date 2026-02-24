from core.database import Base
from datetime import datetime, date, UTC
from enum import Enum as eEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum as sEnum, Text, Boolean, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import Optional
import uuid


class TaskPriority(str, eEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskStatus(str, eEnum):
    TODO = "Todo"
    DOING = "Doing"
    DONE = "Done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(sEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(sEnum(TaskStatus), default=TaskStatus.TODO)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    team = relationship("Team",back_populates="tasks")
    creator = relationship("User",back_populates="created_tasks",foreign_keys=[created_by_id])
    assignee = relationship("User",back_populates="assigned_tasks",foreign_keys=[assignee_id])
