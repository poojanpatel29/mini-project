from core.database import async_get_db
from core.database import get_db
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession 
from schemas.user import UserRead, UserCreate
from models.user import User, UserRole
from core.auth import hash_password
 
router=APIRouter()