"""Service layer for Alerts API."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.risk import Alert, AlertRole, User
from services.domain_audit_service import log_domain_action
from services.forensic_engine import run_forensic_scan


def _role_str(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def _role_filter(user: User):
    role = _role_str(user)
    if role == "admin":
        return None
    if role == "executive":
        return Alert.created_for_role.in_([AlertRole.EXECUTIVE, AlertRole.ALL])
    if role in ("risk_officer", "risk_manager", "department_head"):
        return Alert.created_for_role.in_([AlertRole.RISK_OFFICER, AlertRole.ALL])
    # dept_user (and any others) only see ALL alerts
    return Alert.created_for_role == AlertRole.ALL


async def list_alerts(db: AsyncSession, user: User, limit: int = 200, offset: int = 0) -> Tuple[List[Alert], int]:
    conditions = [Alert.is_dismissed == False]
    rf = _role_filter(user)
    if rf is not None:
        conditions.append(rf)

    where_clause = and_(*conditions)

    total_stmt = select(func.count(Alert.id)).where(where_clause)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        select(Alert)
        .where(where_clause)
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all(), total


async def unread_count(db: AsyncSession, user: User) -> int:
    conditions = [Alert.is_dismissed == False, Alert.is_read == False]
    rf = _role_filter(user)
    if rf is not None:
        conditions.append(rf)

    stmt = select(func.count(Alert.id)).where(and_(*conditions))
    res = await db.execute(stmt)
    return int(res.scalar() or 0)


async def mark_read(db: AsyncSession, alert: Alert, actor_user_id: UUID, request=None) -> Alert:
    prev = {"is_read": alert.is_read}
    alert.is_read = True

    await log_domain_action(
        db,
        entity_type="alert",
        entity_id=alert.id,
        user_id=actor_user_id,
        action="updated",
        previous_values=prev,
        new_values={"is_read": True},
        request=request,
    )

    await db.commit()
    await db.refresh(alert)
    return alert


async def mark_all_read(db: AsyncSession, user: User, actor_user_id: UUID, request=None) -> int:
    rf = _role_filter(user)
    conditions = [Alert.is_dismissed == False]
    if rf is not None:
        conditions.append(rf)

    stmt = (
        update(Alert)
        .where(and_(*conditions))
        .values(is_read=True)
    )
    res = await db.execute(stmt)

    await log_domain_action(
        db,
        entity_type="alert",
        entity_id=UUID(int=0),
        user_id=actor_user_id,
        action="updated",
        previous_values={"scope": "all"},
        new_values={"marked_all_read": True},
        request=request,
    )

    await db.commit()
    return int(res.rowcount or 0)


async def dismiss_alert(db: AsyncSession, alert: Alert, actor_user_id: UUID, request=None) -> Alert:
    prev = {"is_dismissed": alert.is_dismissed}
    alert.is_dismissed = True

    await log_domain_action(
        db,
        entity_type="alert",
        entity_id=alert.id,
        user_id=actor_user_id,
        action="deleted",
        previous_values=prev,
        new_values={"is_dismissed": True},
        request=request,
    )

    await db.commit()
    await db.refresh(alert)
    return alert


async def get_alert(db: AsyncSession, alert_id: UUID) -> Optional[Alert]:
    res = await db.execute(select(Alert).where(Alert.id == alert_id))
    return res.scalar_one_or_none()


async def trigger_forensic_scan(db: AsyncSession) -> List[Alert]:
    # run_forensic_scan creates and commits alerts; we just return newly created ones.
    return await run_forensic_scan(db)
