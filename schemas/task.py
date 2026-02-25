# schemas/task.py

from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from enum import Enum
from datetime import datetime
from typing import List, Optional
from models.task import TaskPriority, TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    team_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None

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
    task_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[UUID] = None
    is_deleted: Optional[bool] = None

class AssignTaskRequest(BaseModel):
    task_id: UUID
    team_id: UUID
    employee_id: UUID


class TaskBulkCreate(BaseModel):
    tasks: List[TaskCreate] = Field(..., min_length=1)
 
    @field_validator("tasks")
    def check_max_batch_size(cls, v: List[TaskCreate]) -> List[TaskCreate]:
        if len(v) > 50:
            raise ValueError("Bulk create limit is 50 tasks per request")
        return v
 
 
class TaskBulkDelete(BaseModel):
    task_ids: List[UUID] = Field(..., min_length=1)
 
    @field_validator("task_ids")
    def check_max_batch_size(cls, v: List[UUID]) -> List[UUID]:
        if len(v) > 50:
            raise ValueError("Bulk delete limit is 50 tasks per request")
        return v