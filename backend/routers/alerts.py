"""Alerts API router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_roles
from models.risk import Alert, User
from schemas.alert import AlertListResponse, AlertResponse, UnreadCountResponse
from services.alerts_service import (
    dismiss_alert,
    get_alert,
    list_alerts,
    mark_all_read,
    mark_read,
    trigger_forensic_scan,
    unread_count,
)
from utils.db_dep import get_db

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


def _to_response(a: Alert) -> AlertResponse:
    return AlertResponse(
        id=a.id,
        alert_type=str(a.alert_type.value if hasattr(a.alert_type, "value") else a.alert_type),
        risk_id=a.risk_id,
        message=a.message,
        severity=str(a.severity.value if hasattr(a.severity, "value") else a.severity),
        is_read=bool(a.is_read),
        is_dismissed=bool(a.is_dismissed),
        created_for_role=str(a.created_for_role.value if hasattr(a.created_for_role, "value") else a.created_for_role),
        created_at=a.created_at,
    )


@router.get("", response_model=AlertListResponse)
async def list_alerts_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertListResponse:
    items, total = await list_alerts(db, current_user)
    return AlertListResponse(items=[_to_response(a) for a in items], total=total)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnreadCountResponse:
    return UnreadCountResponse(unread=await unread_count(db, current_user))


@router.patch("/{alert_id}/read", response_model=AlertResponse)
async def mark_read_endpoint(
    request: Request,
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    alert = await get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert = await mark_read(db, alert, actor_user_id=current_user.id, request=request)
    return _to_response(alert)


@router.patch("/read-all")
async def mark_all_read_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await mark_all_read(db, current_user, actor_user_id=current_user.id, request=request)
    return {"updated": count}


@router.delete("/{alert_id}", response_model=AlertResponse)
async def dismiss_alert_endpoint(
    request: Request,
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    alert = await get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert = await dismiss_alert(db, alert, actor_user_id=current_user.id, request=request)
    return _to_response(alert)


@router.post("/forensic-scan")
async def forensic_scan_now(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "risk_officer", "risk_manager")),
):
    created = await trigger_forensic_scan(db)
    return {"created": len(created)}
