from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


# Base schema with common attributes
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


# Schema for creating a new user (registration)
class UserCreate(UserBase):
    password: str


# Schema for updating user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


# Schema for user response (what API returns)
class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


# Schema for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schema for token data
class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
