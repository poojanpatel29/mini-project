from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class TeamCreate(BaseModel):
    name: str

class TeamRead(BaseModel):
    id: UUID
    name: str
    created_by_id: UUID
    is_deleted: bool

    model_config = {
        "from_attributes": True
    }

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None