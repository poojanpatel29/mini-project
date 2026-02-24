from core.database import async_get_db
from core.database import get_db
from core.auth import create_access_token, hash_password, get_current_user, require_roles, verify_password
from datetime import datetime, UTC
from fastapi import Depends, APIRouter, HTTPException
from models.user import User, UserRole
from models.task import Task,TaskPriority,TaskStatus
from models.userteam import UserTeam
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from schemas.user import UserLogin, UserRead, UserCreate, TokenResponse
from schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()


@router.post("/admin", response_model=UserRead | dict)
async def create_admin(db: AsyncSession = Depends(async_get_db)):
    hashed_password = hash_password("admin@1")
    user = {
        "name": "admin1",
        "email": "admin1@gmail.com",
        "password": hashed_password,
        "role": UserRole.ADMIN,
    }

    db_user = User(**user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    db.close()

    return {"message": "Created Successfully"}


@router.post("/signup")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("Admin", "Manager")),
):

    if current_user.role == UserRole.ADMIN:
        role = user.role

    if current_user.role == UserRole.MANAGER:
        role = UserRole.EMPLOYEE

    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": f"{user.role} Created Successfully"}

@router.post("/login", response_model=TokenResponse)
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(async_get_db),
):
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    access_token = create_access_token(db_user.id)

    return TokenResponse(
        token=access_token,
        role=db_user.role,
    )

@router.post("/tasks", response_model=TaskRead, status_code=201)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("Admin", "Manager")),
):
    if current_user.role == UserRole.MANAGER:
        owner_id = current_user.id

    else:
        if not task.manager_id:
            raise HTTPException(
                status_code=400,
                detail="manager_id required when admin creates task",
            )

        manager = (
            await db.execute(
                select(User).where(
                    User.id == task.manager_id,
                    User.role == UserRole.MANAGER,
                )
            )
        ).scalar_one_or_none()

        if not manager:
            raise HTTPException(
                status_code=400,
                detail="Invalid manager_id",
            )

        owner_id = manager.id

    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        team_id=task.team_id,
        created_by_id=owner_id,
        assignee_id=task.assignee_id,
        is_deleted=False,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task