from Core.database import Base
from enum import Enum as eEnum
from sqlalchemy import Enum as sEnum, Boolean, UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from typing import List
import uuid


class UserRole(str, eEnum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    EMPLOYEE = "Employee"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    teams = relationship(
        "Team", secondary="user_teams", back_populates="members", lazy="selectin"
    )
    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by_id",
        lazy="selectin",
    )
    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
        lazy="selectin",
    )
    activity_logs = relationship("ActivityLog", back_populates="user", lazy="selectin")
