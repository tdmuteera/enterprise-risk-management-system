"""Pydantic schemas for Risk endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=3)
    category: str
    department_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None

    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    velocity: int = Field(ge=1, le=5)
    detectability: int = Field(ge=1, le=5)


class RiskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, min_length=3)
    category: Optional[str] = None
    department_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None

    likelihood: Optional[int] = Field(default=None, ge=1, le=5)
    impact: Optional[int] = Field(default=None, ge=1, le=5)
    velocity: Optional[int] = Field(default=None, ge=1, le=5)
    detectability: Optional[int] = Field(default=None, ge=1, le=5)

    status: Optional[str] = None


class RiskOut(BaseModel):
    id: UUID
    title: str
    description: str
    category: str
    department_id: UUID
    owner_id: UUID

    likelihood: int
    impact: int
    velocity: int
    detectability: int

    risk_score: float
    status: str
    institutional_risk_index: Optional[float] = None

    created_at: datetime
    updated_at: datetime

    recommendations: List[str] = []


class RiskHistoryOut(BaseModel):
    id: UUID
    risk_id: UUID
    action: str
    changed_by_id: UUID
    changed_at: datetime
    previous_values: dict
    new_values: dict
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
