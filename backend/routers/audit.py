"""Audit Logs API.

Provides paginated access to RiskHistory and DomainAuditEvent records
for risk officers and admins.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.dependencies import get_current_user, require_roles
from models.risk import (
    DomainAuditEvent,
    Risk,
    RiskHistory,
    User,
)
from utils.db_dep import get_db

router = APIRouter(prefix="/api/v1/audit-logs", tags=["Audit Logs"])


def _role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    id: UUID
    source: str  # "risk_history" or "domain_audit"
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    risk_id: Optional[UUID] = None
    risk_title: Optional[str] = None
    action: str
    changed_by_id: UUID
    changed_by_name: Optional[str] = None
    changed_by_email: Optional[str] = None
    changed_at: datetime
    previous_values: Dict[str, Any] = Field(default_factory=dict)
    new_values: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogListResponse(BaseModel):
    items: List[AuditLogEntry]
    total: int
    page: int
    page_size: int


@router.get(
    "",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_roles("admin", "risk_officer", "risk_manager", "department_head"))],
)
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_filter: Optional[str] = Query(None, description="Filter by user email or name (partial match)"),
    action_filter: Optional[str] = Query(None, description="Filter by action type"),
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter to this date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> AuditLogListResponse:
    """Return paginated audit log entries from RiskHistory with user and risk info."""

    # Build base query with joins
    stmt = (
        select(RiskHistory, User.full_name, User.email, Risk.title)
        .join(User, User.id == RiskHistory.changed_by_id)
        .join(Risk, Risk.id == RiskHistory.risk_id)
    )

    conditions = []

    if _role(current_user) == "department_head":
        if not current_user.department_id:
            raise HTTPException(status_code=403, detail="Department heads must belong to a department")
        conditions.append(Risk.department_id == current_user.department_id)

    if user_filter:
        like_pattern = f"%{user_filter}%"
        conditions.append(
            or_(
                User.full_name.ilike(like_pattern),
                User.email.ilike(like_pattern),
            )
        )

    if action_filter:
        conditions.append(RiskHistory.action == action_filter)

    if start_date:
        conditions.append(RiskHistory.changed_at >= start_date)

    if end_date:
        conditions.append(RiskHistory.changed_at <= end_date)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Count total
    count_stmt = (
        select(func.count(RiskHistory.id))
        .join(User, User.id == RiskHistory.changed_by_id)
        .join(Risk, Risk.id == RiskHistory.risk_id)
    )
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))

    total = int((await db.execute(count_stmt)).scalar_one())

    # Paginated results
    stmt = stmt.order_by(desc(RiskHistory.changed_at)).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    rows = result.all()

    items: List[AuditLogEntry] = []
    for history, user_name, user_email, risk_title in rows:
        items.append(
            AuditLogEntry(
                id=history.id,
                source="risk_history",
                entity_type="risk",
                entity_id=history.risk_id,
                risk_id=history.risk_id,
                risk_title=risk_title,
                action=str(history.action.value if hasattr(history.action, "value") else history.action),
                changed_by_id=history.changed_by_id,
                changed_by_name=user_name,
                changed_by_email=user_email,
                changed_at=history.changed_at,
                previous_values=history.previous_values or {},
                new_values=history.new_values or {},
                ip_address=history.ip_address,
                user_agent=history.user_agent,
            )
        )

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/domain",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_roles("admin", "risk_officer", "risk_manager"))],
)
async def list_domain_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g., department, user, alert)"),
    user_filter: Optional[str] = Query(None, description="Filter by user email or name"),
    action_filter: Optional[str] = Query(None, description="Filter by action type"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> AuditLogListResponse:
    """Return paginated domain audit event entries."""

    stmt = (
        select(DomainAuditEvent, User.full_name, User.email)
        .join(User, User.id == DomainAuditEvent.changed_by_id)
    )

    conditions = []

    if entity_type:
        conditions.append(DomainAuditEvent.entity_type == entity_type)

    if user_filter:
        like_pattern = f"%{user_filter}%"
        conditions.append(
            or_(
                User.full_name.ilike(like_pattern),
                User.email.ilike(like_pattern),
            )
        )

    if action_filter:
        conditions.append(DomainAuditEvent.action == action_filter)

    if start_date:
        conditions.append(DomainAuditEvent.changed_at >= start_date)

    if end_date:
        conditions.append(DomainAuditEvent.changed_at <= end_date)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = (
        select(func.count(DomainAuditEvent.id))
        .join(User, User.id == DomainAuditEvent.changed_by_id)
    )
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))

    total = int((await db.execute(count_stmt)).scalar_one())

    stmt = stmt.order_by(desc(DomainAuditEvent.changed_at)).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    rows = result.all()

    items: List[AuditLogEntry] = []
    for event, user_name, user_email in rows:
        items.append(
            AuditLogEntry(
                id=event.id,
                source="domain_audit",
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                risk_id=None,
                risk_title=None,
                action=event.action,
                changed_by_id=event.changed_by_id,
                changed_by_name=user_name,
                changed_by_email=user_email,
                changed_at=event.changed_at,
                previous_values=event.previous_values or {},
                new_values=event.new_values or {},
                ip_address=event.ip_address,
                user_agent=event.user_agent,
            )
        )

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
