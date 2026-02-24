from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserTeamRead(BaseModel):
    user_id: UUID
    team_id: UUID
    joined_at: datetime

    model_config = {
        "from_attributes": True
    }


class AssignEmployeeRequest(BaseModel):
    team_id: UUID
    employee_id: UUID