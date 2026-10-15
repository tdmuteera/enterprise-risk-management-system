"""Pydantic schemas for Risk CRUD API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ColourBand(BaseModel):
    label: str
    hex: str
    tailwind: str


class RiskLinkSummary(BaseModel):
    linked_risk_id: UUID
    title: str
    department_id: UUID
    department_name: Optional[str] = None
    link_type: str
    weight: float
    notes: Optional[str] = None

    risk_score: float
    normalised_score: float
    colour_band: ColourBand


class UserSummary(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    department_id: Optional[UUID] = None


class RiskHistoryEntry(BaseModel):
    id: UUID
    risk_id: UUID
    action: str
    changed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    previous_values: dict[str, Any] = Field(default_factory=dict)
    new_values: dict[str, Any] = Field(default_factory=dict)

    user: Optional[UserSummary] = None


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

    risk_type: Optional[str] = Field(default="Inherent")
    parent_risk_id: Optional[UUID] = None


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
    review_justification: Optional[str] = None


class RiskResponse(BaseModel):
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
    normalised_score: float
    colour_band: ColourBand

    status: str
    risk_type: Optional[str] = None
    parent_risk_id: Optional[UUID] = None
    reviewer_id: Optional[UUID] = None
    review_justification: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    iri: Optional[float] = None

    created_at: datetime
    updated_at: datetime

    recommendations: List[str] = Field(default_factory=list)
    linked_risks: List[RiskLinkSummary] = Field(default_factory=list)
    mitigation_count: int = 0
    overdue_mitigations: int = 0


class RiskDetailResponse(RiskResponse):
    audit_trail: List[RiskHistoryEntry] = Field(default_factory=list)


class RiskListResponse(BaseModel):
    items: List[RiskResponse]
    total: int
    page: int
    page_size: int
    top_5: List[RiskResponse]


class ReviewJustification(BaseModel):
    justification: str = Field(min_length=3, max_length=2000)


class RiskLinkCreate(BaseModel):
    target_risk_id: UUID
    link_type: str
    weight: float = Field(ge=0.0, le=1.0)
    notes: Optional[str] = None
