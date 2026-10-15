"""Generic immutable domain audit logging.

RiskHistory is strictly tied to Risk (risk_id is NOT NULL). For other domain
entities (departments, users, alerts, mitigations), we use DomainAuditEvent.

This stays append-only: always insert, never update/delete.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from models.risk import DomainAuditEvent
from utils.json_utils import compute_json_diff


async def log_domain_action(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    user_id: UUID,
    action: str,
    previous_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> DomainAuditEvent:
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    if request:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            ip_address = xff.split(",")[0].strip() or None
        else:
            ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    previous_values = previous_values or {}
    new_values = new_values or {}

    if action == "created":
        stored_previous: Dict[str, Any] = {}
        stored_new: Dict[str, Any] = new_values
    elif action == "deleted":
        stored_previous = previous_values
        stored_new = {}
    else:
        diff = compute_json_diff(previous_values, new_values)
        stored_previous = {}
        stored_new = {}

        for key, change in diff.get("modified", {}).items():
            stored_previous[key] = change.get("from")
            stored_new[key] = change.get("to")

        for key, value in diff.get("added", {}).items():
            stored_previous[key] = None
            stored_new[key] = value

        for key, value in diff.get("removed", {}).items():
            stored_previous[key] = value
            stored_new[key] = None

    ev = DomainAuditEvent(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changed_by_id=user_id,
        changed_at=datetime.utcnow(),
        previous_values=stored_previous,
        new_values=stored_new,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(ev)
    await db.flush()
    return ev
