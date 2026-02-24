from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum
from typing import Optional
from models.user import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = None

class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    role: UserRole