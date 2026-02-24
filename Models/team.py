from Core.database import Base
from sqlalchemy import ForeignKey, Boolean, UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import uuid


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
 
    name: Mapped[str] = mapped_column(nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)

    members = relationship(
        "User", secondary="user_teams", back_populates="teams", lazy="selectin"
    )
    tasks = relationship("Task", back_populates="team", lazy="selectin")
    invites = relationship("InviteToken", back_populates="team", lazy="selectin")
