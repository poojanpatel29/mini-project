from logging.config import dictConfig
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_get_db
from models.team import Team
from models.userteam import UserTeam
from models.user import User, UserRole
from models.task import Task
from schemas.team import TeamRead
from core.auth import get_current_user

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
