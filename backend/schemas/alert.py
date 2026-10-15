"""Pydantic schemas for Alerts API."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: UUID
    alert_type: str
    risk_id: Optional[UUID] = None
    message: str
    severity: str
    is_read: bool
    is_dismissed: bool
    created_for_role: str
    created_at: datetime


class AlertListResponse(BaseModel):
    items: List[AlertResponse] = Field(default_factory=list)
    total: int


class UnreadCountResponse(BaseModel):
    unread: int
