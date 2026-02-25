from logging.config import dictConfig
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_get_db
from models.team import Team
from models.userteam import UserTeam
from models.user import User, UserRole
from models.task import Task
from schemas.team import TeamRead
from  schemas.task import TaskBulkDelete
from core.auth import get_current_user, require_roles

router = APIRouter()


@router.delete("/teams/{team_id}", response_model=dict)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    team = (
        await db.execute(
            select(Team).where(
                Team.id == team_id,
                Team.is_deleted == False,
            )
        )
    ).scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if current_user.role == UserRole.ADMIN or (
        current_user.role == UserRole.MANAGER and team.created_by_id == current_user.id
    ):
        team.is_deleted = True
        await db.commit()
        return {"message": "deleted successfully"}
    raise HTTPException(
        status_code=403, detail="if you are manager then you only delete your team"
    )


@router.delete("/task/{task_id}", response_model=dict)
async def get_team(
    task_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.is_deleted == False,
            )
        )
    ).scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role == UserRole.ADMIN or (
        current_user.role == UserRole.MANAGER and task.created_by_id == current_user.id
    ):
        task.is_deleted = True
        await db.commit()
        return {"message": "deleted successfully"}

    raise HTTPException(
        status_code=403, detail="if you are manager then you only delete your team"
    )


@router.delete("/bulk-delete")
async def bulk_delete_tasks(
    data: TaskBulkDelete,
    user: User = Depends(require_roles("Admin", "Manager")),
    db: AsyncSession = Depends(async_get_db),
):
    try:
        fetch_query = select(Task).where(Task.id.in_(data.task_ids))
        fetch_result = await db.execute(fetch_query)
        existing_tasks = fetch_result.scalars().all()
        existing_ids = {t.id for t in existing_tasks}
 
        if len(existing_ids) != len(data.task_ids):
            raise HTTPException(
                status_code=404, detail="Kuch task IDs database mein nahi mile"
            )
 
        if user.role == "manager":
            unauthorized_tasks = [
                t for t in existing_tasks if t.created_by_id != user.id
            ]
            if unauthorized_tasks:
                raise HTTPException(
                    status_code=403,
                    detail="Aap kisi aur manager ki task delete nahi kar sakte",
                )
 
        delete_query = delete(Task).where(Task.id.in_(data.task_ids))
        await db.execute(delete_query)
        await db.commit()
 
        return {"message": "Bulk delete successful"}
 
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error during bulk delete {e}")