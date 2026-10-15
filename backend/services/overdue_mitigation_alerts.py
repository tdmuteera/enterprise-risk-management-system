"""Scheduled job: raise alerts for overdue mitigations (at most one per risk per day)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.risk import Alert, AlertRole, AlertSeverity, AlertType, MitigationAction, MitigationStatus


async def create_overdue_mitigation_alerts(db: AsyncSession) -> int:
    """
    For each incomplete mitigation past due_date, create an OverdueMitigation alert
    if none exists for that risk yet today (UTC).
    """
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    stmt = select(MitigationAction).where(
        and_(
            MitigationAction.due_date < now,
            MitigationAction.status != MitigationStatus.COMPLETED,
        )
    )
    res = await db.execute(stmt)
    overdue = res.scalars().all()

    created = 0
    for m in overdue:
        exists_stmt = (
            select(func.count(Alert.id))
            .where(
                and_(
                    Alert.alert_type == AlertType.OVERDUE_MITIGATION,
                    Alert.risk_id == m.risk_id,
                    Alert.created_at >= start_of_day,
                )
            )
        )
        exists_res = await db.execute(exists_stmt)
        if int(exists_res.scalar() or 0) > 0:
            continue

        alert = Alert(
            alert_type=AlertType.OVERDUE_MITIGATION,
            risk_id=m.risk_id,
            message=f"Mitigation overdue: {m.description[:500]}",
            severity=AlertSeverity.WARNING,
            is_read=False,
            is_dismissed=False,
            created_for_role=AlertRole.ALL,
        )
        db.add(alert)
        created += 1

    if created:
        await db.commit()
    return created
