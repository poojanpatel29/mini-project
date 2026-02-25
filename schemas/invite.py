from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class InviteCreate(BaseModel):
    team_id: UUID
    user_email:EmailStr

class InviteRead(BaseModel):
    id: Optional[UUID] = None
    team_id: UUID
    expires_at: datetime
    is_used: bool
    

    model_config = {
        "from_attributes": True
    }