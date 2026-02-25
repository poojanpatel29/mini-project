from core.database import async_get_db
from core.database import get_db
from core.auth import hash_password, require_roles, get_current_user
from fastapi import Depends, APIRouter, HTTPException
from models.user import User, UserRole
from models.team import Team
from models.task import Task
from models.userteam import UserTeam
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import func, select
from schemas.user import UserRead, UserCreate
from schemas.team import *
from uuid import UUID

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(
    user: User = Depends(require_roles("Admin", "Manager", "Employee")),
    db: AsyncSession = Depends(async_get_db),
):
    return user


@router.get("/all", response_model=list[UserRead])
async def get_all_users(
    user: User = Depends(require_roles("Admin")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(User)
    result = await db.execute(query)
    result = result.scalars().all()
    db.close()
    return result


@router.get("/all_teams", response_model=list[TeamRead])
async def list_teams(
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        teams = (
            (await db.execute(select(Team).where(Team.is_deleted == False)))
            .scalars()
            .all()
        )
        return teams

    if current_user.role == UserRole.MANAGER:
        teams = (
            (
                await db.execute(
                    select(Team).where(
                        Team.created_by_id == current_user.id,
                        Team.is_deleted == False,
                    )
                )
            )
            .scalars()
            .all()
        )
        return teams

    teams = (
        (
            await db.execute(
                select(Team)
                .join(UserTeam, Team.id == UserTeam.team_id)
                .where(
                    UserTeam.user_id == current_user.id,
                    Team.is_deleted == False,
                )
            )
        )
        .scalars()
        .all()
    )

    return teams


@router.get("/tasks/stats")
async def get_task_stats(
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = select(Task.status, func.count(Task.id)).where(
        Task.is_deleted == False
    )

    if current_user.role == UserRole.ADMIN:
        query = base_query.group_by(Task.status)

    elif current_user.role == UserRole.MANAGER:
        subquery = select(Team.id).where(
            Team.created_by_id == current_user.id,
            Team.is_deleted == False,
        )

        query = (
            base_query
            .where(Task.team_id.in_(subquery))
            .group_by(Task.status)
        )

    else:
        subquery = select(UserTeam.team_id).where(
            UserTeam.user_id == current_user.id
        )

        query = (
            base_query
            .where(Task.team_id.in_(subquery))
            .group_by(Task.status)
        )

    result = await db.execute(query)
    rows = result.all()

    stats = {status.name: 0 for status in TaskStatus}

    for status, count in rows:
        stats[status.name] = count

    return stats


@router.get("/teams/{team_id}", response_model=TeamDetailResponse)
async def get_team_details(
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

    if current_user.role == UserRole.ADMIN:
        pass

    elif current_user.role == UserRole.MANAGER:
        if team.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        membership = (
            await db.execute(
                select(UserTeam).where(
                    UserTeam.team_id == team_id,
                    UserTeam.user_id == current_user.id,
                )
            )
        ).scalar_one_or_none()

        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")

    task_count = (
        await db.execute(
            select(func.count(Task.id)).where(
                Task.team_id == team_id,
                Task.is_deleted == False,
            )
        )
    ).scalar()

    member_count = (
        await db.execute(
            select(func.count(UserTeam.user_id)).where(
                UserTeam.team_id == team_id,
            )
        )
    ).scalar()

    manager = (
        await db.execute(select(User).where(User.id == team.created_by_id))
    ).scalar_one()

    members = (
        (
            await db.execute(
                select(User)
                .join(UserTeam, User.id == UserTeam.user_id)
                .where(UserTeam.team_id == team_id)
            )
        )
        .scalars()
        .all()
    )

    members_data = []

    for member in members:
        user_task_count = (
            await db.execute(
                select(func.count(Task.id)).where(
                    Task.assignee_id == member.id,
                    Task.team_id == team_id,
                    Task.is_deleted == False,
                )
            )
        ).scalar()

        members_data.append(
            TeamMemberStats(
                id=member.id,
                name=member.name,
                email=member.email,
                task_count=user_task_count,
            )
        )

    return TeamDetailResponse(
        team_id=team.id,
        team_name=team.name,
        task_count=task_count,
        member_count=member_count,
        manager=ManagerDetails(
            id=manager.id,
            name=manager.name,
            email=manager.email,
        ),
        members=members_data,
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: UUID,
    user: User = Depends(require_roles("Admin", "Manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    result = result.scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail="User not Found")

    return result
