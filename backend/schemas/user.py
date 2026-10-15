"""Pydantic schemas for Users API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="dept_user")
    department_id: Optional[UUID] = None
    is_active: bool = True


class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    role: Optional[str] = None
    department_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UserUpdateSelf(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    department_id: Optional[UUID] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
