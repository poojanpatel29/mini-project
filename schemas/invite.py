from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class InviteCreate(BaseModel):
    team_id: UUID

class InviteRead(BaseModel):
    id: UUID
    team_id: UUID
    created_by_id: UUID
    expires_at: datetime
    is_used: bool

    model_config = {
        "from_attributes": True
    }