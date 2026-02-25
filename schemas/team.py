from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

class TeamCreate(BaseModel):
    name: str
    manager_id: Optional[UUID] = None

class TeamRead(BaseModel):
    id: UUID
    name: str
    created_by_id: UUID
    is_deleted: bool

    model_config = {
        "from_attributes": True
    }

class TeamUpdate(BaseModel):
    team_id: Optional[UUID] = None
    name: Optional[str] = None
    is_deleted: Optional[bool] = None


class TeamMemberStats(BaseModel):
    id: UUID
    name: str
    email: str
    task_count: int


class ManagerDetails(BaseModel):
    id: UUID
    name: str
    email: str


class TeamDetailResponse(BaseModel):
    team_id: UUID
    team_name: str
    task_count: int
    member_count: int
    manager: ManagerDetails
    members: List[TeamMemberStats]