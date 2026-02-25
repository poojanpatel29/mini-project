from typing import List

from core.database import async_get_db
from core.database import get_db
from core.auth import hash_password, require_roles
from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks
from models.user import User, UserRole
from models.task import Task
from models.team import Team
from models.userteam import UserTeam
from sqlalchemy.ext.asyncio.session import AsyncSession
from schemas.user import UserRead, UserCreate, UserUpdate
from schemas.task import AssignTaskRequest, TaskRead, TaskUpdate
from schemas.team import TeamCreate, TeamRead, TeamUpdate
from sqlalchemy import select
from utils.helper import send_task_completion_email

router = APIRouter()


@router.patch("/tasks_assign", status_code=200)
async def assign_task_to_member(
    data: AssignTaskRequest,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("Manager")),
):
    task = (
        await db.execute(
            select(Task).where(
                Task.id == data.task_id,
                Task.is_deleted == False,
            )
        )
    ).scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.team_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Task is already assigned to a team",
        )

    team = (
        await db.execute(
            select(Team).where(
                Team.id == data.team_id,
                Team.is_deleted == False,
            )
        )
    ).scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team.created_by_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="This team does not belong to you",
        )

    membership = (
        await db.execute(
            select(UserTeam).where(
                UserTeam.team_id == data.team_id,
                UserTeam.user_id == data.employee_id,
            )
        )
    ).scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=400,
            detail="Employee is not a member of this team",
        )

    task.team_id = data.team_id
    task.assignee_id = data.employee_id

    await db.commit()
    await db.refresh(task)

    return {"message": "Task assigned successfully"}


@router.patch("/update_task", response_model=TaskRead)
async def update_task(
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_roles("Admin", "Manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(Task).where(Task.id == task_data.task_id)
    existing_record = (await db.execute(query)).scalars().first()

    if not existing_record:
        raise HTTPException(status_code=404, detail="Task not Found")

    if existing_record.created_by_id != user.id:
        raise HTTPException(status_code=403, detail="You can only update your task")

    old_status = existing_record.status

    if task_data.title:
        existing_record.title = task_data.title

    if task_data.description:
        existing_record.description = task_data.description

    if task_data.priority:
        existing_record.priority = task_data.priority

    if task_data.status:
        existing_record.status = task_data.status

    if task_data.assignee_id:
        existing_record.assignee_id = task_data.assignee_id

    await db.commit()
    await db.refresh(existing_record)

    if (
        task_data.status
        and task_data.status.name == "DONE"
        and old_status.name != "DONE"
        and existing_record.assignee_id
    ):
        assignee = (
            await db.execute(
                select(User).where(User.id == existing_record.assignee_id)
            )
        ).scalar_one_or_none()

        if assignee:
            background_tasks.add_task(
                send_task_completion_email,
                assignee.email,
                existing_record.title,
            )

    return existing_record

@router.patch("/update_team", response_model=TeamRead)
async def update_team(
    team_data: TeamUpdate,
    user: User = Depends(require_roles("Admin", "Manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(Team).where(Team.id == team_data.team_id)
    existing_record = await db.execute(query)
    existing_record = existing_record.scalars().first()

    if not existing_record:
        raise HTTPException(status_code=404, detail="Team not found")

    if user.role == UserRole.MANAGER and existing_record.created_by_id != user.id:
        raise HTTPException(
            status_code=403, detail="You can only update your team details."
        )

    if team_data.name:
        existing_record.name = team_data.name

    await db.commit()
    await db.refresh(existing_record)
    db.close()
    return existing_record


@router.patch("/update_user", response_model=UserRead)
async def update_user(
    update_data: UserUpdate,
    user: User = Depends(require_roles("Admin", "Manager", "Employee")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(User).where(User.id == update_data.user_id)
    result = await db.execute(query)
    result = result.scalars().first()
 
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
 
    if user.role != "Admin" and update_data.role is not None:
        raise HTTPException(status_code=403, detail="Only admin can change role.")
 
    if result.role == "Admin":
        raise HTTPException(status_code=400, detail="You cannot change Admin's role.")
 
    if result.role == update_data.role:
        raise HTTPException(status_code=400, detail="The user has same role as of now.")
 
    if result.role == "Manager" and update_data.role == "Employee":
        raise HTTPException(status_code=400, detail="Cannot demote User")
 
    if result.role == "Manager" and update_data.role == "Admin":
        raise HTTPException(status_code=400, detail="Highest Level reached")
   
    if user.role in ["Admin","Manager"] and update_data.role!="Admin":
        if update_data.is_active is not None:
            result.is_active=update_data.is_active

    if update_data.name and update_data.user_id != user.id:
        raise HTTPException(status_code=403, detail="Only employee can change his/her name.")
   
    if update_data.user_id==user.id and update_data.name:
        result.name=update_data.name
   
    if update_data.role:
        result.role=update_data.role
    await db.commit()
    await db.refresh(result)
    return result

@router.patch("/bulk-update", response_model=List[TaskRead])
async def bulk_update_tasks(
    updates: List[TaskUpdate],
    user: User = Depends(require_roles("Admin", "Manager")),
    db: AsyncSession = Depends(async_get_db),
):
    if not updates:
        raise HTTPException(status_code=400, detail="Update list cannot be empty")
 
    task_ids = [u.task_id for u in updates]
    query = select(Task).where(Task.id.in_(task_ids))
    result = await db.execute(query)
    existing_tasks = {t.id: t for t in result.scalars().all()}
 
    if len(existing_tasks) != len(task_ids):
        raise HTTPException(status_code=404, detail="Some of the task Ids are not available.")
 
    updated_objects = []
    for update_data in updates:
        target_task = existing_tasks.get(update_data.task_id)
 
        if user.role == "Manager" and target_task.created_by_id != user.id:
            raise HTTPException(
                status_code=403,
                detail=f"Task {target_task.id} is not yours"
            )
 
        update_dict = update_data.model_dump(exclude_unset=True, exclude={"task_id"})
        for key, value in update_dict.items():
            setattr(target_task, key, value)
 
        updated_objects.append(target_task)
 
    try:
        await db.commit()
        for t in updated_objects:
            await db.refresh(t)
        return updated_objects
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Bulk update failed")