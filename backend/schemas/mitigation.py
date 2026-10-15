"""Pydantic schemas for Mitigations API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MitigationCreate(BaseModel):
    description: str = Field(min_length=2, max_length=5000)
    due_date: datetime
    assigned_to_id: UUID


class MitigationUpdate(BaseModel):
    status: Optional[str] = None
    completion_date: Optional[datetime] = None
    effectiveness_score: Optional[int] = Field(default=None, ge=1, le=5)
    description: Optional[str] = Field(default=None, min_length=2, max_length=5000)
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[UUID] = None


class MitigationResponse(BaseModel):
    id: UUID
    risk_id: UUID
    description: str
    assigned_to_id: UUID
    due_date: datetime
    completion_date: Optional[datetime] = None
    status: str
    effectiveness_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
