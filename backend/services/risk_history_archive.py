"""Move old RiskHistory rows into risk_history_archive (scheduled job)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models_complete import RiskHistory, RiskHistoryArchive


async def archive_risk_history_older_than(
    db: AsyncSession,
    *,
    retention_years: int = 2,
    batch_size: int = 2000,
) -> int:
    """
    Copy rows older than ``retention_years`` into ``risk_history_archive`` and delete from ``risk_history``.

    Returns:
        Number of rows archived (and removed from the hot table).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=365 * retention_years)

    stmt = (
        select(RiskHistory)
        .where(RiskHistory.changed_at < cutoff)
        .order_by(RiskHistory.changed_at.asc())
        .limit(batch_size)
    )
    res = await db.execute(stmt)
    rows = res.scalars().all()
    if not rows:
        return 0

    now = datetime.now(timezone.utc)
    for r in rows:
        db.add(
            RiskHistoryArchive(
                id=r.id,
                risk_id=r.risk_id,
                action=r.action,
                changed_by_id=r.changed_by_id,
                changed_at=r.changed_at,
                previous_values=r.previous_values,
                new_values=r.new_values,
                ip_address=r.ip_address,
                user_agent=r.user_agent,
                archived_at=now,
            )
        )

    ids = [r.id for r in rows]
    await db.execute(delete(RiskHistory).where(RiskHistory.id.in_(ids)))
    await db.commit()
    return len(rows)
