from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserSchema(BaseModel):
    """Pydantic model for validating incoming user registration data."""
    full_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=20)


class UserResponse(BaseModel):
    """Pydantic model for serializing user data in responses."""
    id: int = 1
    full_name: str
    email: EmailStr
    avatar: str | None
    role: Role
    picture_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Pydantic model for validating incoming user update data."""
    full_name: str
    email: EmailStr
    password: str


class AnotherUsers(BaseModel):
    """Pydantic model for serializing simplified user data in responses."""
    full_name: str
    email: EmailStr
    avatar: str
    picture_count: Optional[int]
    created_at: datetime


class TokenSchema(BaseModel):
    """Pydantic model for serializing JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
