"""Pydantic schemas for Departments API."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.risk import RiskResponse


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    code: str = Field(min_length=2, max_length=4)
    description: Optional[str] = Field(default=None, max_length=5000)
    head_of_dept: Optional[str] = Field(default=None, max_length=255)


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    code: Optional[str] = Field(default=None, min_length=2, max_length=4)
    description: Optional[str] = Field(default=None, max_length=5000)
    head_of_dept: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str] = None
    head_of_dept: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DepartmentDetailResponse(DepartmentResponse):
    open_risks_count: int = 0
    iri: Optional[float] = None


class DepartmentTrendEntry(BaseModel):
    day: date
    created: int = 0
    updated: int = 0
    closed: int = 0


class DepartmentSummaryResponse(BaseModel):
    total_risks: int
    critical: int
    high: int
    medium: int
    low: int
    top5_risks: List[RiskResponse] = Field(default_factory=list)
    iri: Optional[float] = None
    trend: List[DepartmentTrendEntry] = Field(default_factory=list)
