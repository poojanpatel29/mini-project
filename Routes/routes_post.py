from core.database import async_get_db
from core.database import get_db
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession 
from schemas.user import UserRead, UserCreate
from models.user import User, UserRole
from core.auth import hash_password
 
router=APIRouter()
 
@router.post('/admin',response_model=UserRead|dict)
async def create_admin(db:AsyncSession=Depends(async_get_db)):
    hashed_password = hash_password("admin@1")
    user={
        "name":"admin1",
        "email":"admin1@gmail.com",
        "password":hashed_password,
        "role": UserRole.ADMIN
    }
 
    db_user=User(**user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    db.close()
   
    return {"message":"Created Successfully"}