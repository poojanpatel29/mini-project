from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ActivityRead(BaseModel):
    id: UUID
    user_id: UUID
    action_type: str
    resource_id: int
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }