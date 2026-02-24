# schemas/task.py

from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from datetime import datetime
from typing import Optional
from models.task import TaskPriority, TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    team_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None

class TaskRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    team_id: Optional[UUID]
    created_by_id: UUID
    assignee_id: Optional[UUID]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[UUID] = None
    is_deleted: Optional[bool] = None