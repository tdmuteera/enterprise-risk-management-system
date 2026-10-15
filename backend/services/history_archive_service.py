"""Archive old RiskHistory rows into risk_history_archive."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.risk import RiskHistory, RiskHistoryArchive


async def archive_risk_history_older_than(db: AsyncSession, years: int = 2) -> int:
    """
    Move RiskHistory records older than ``years`` into RiskHistoryArchive and delete originals.

    Returns number of rows archived.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=365 * years)

    result = await db.execute(select(RiskHistory).where(RiskHistory.changed_at < cutoff))
    rows = result.scalars().all()
    if not rows:
        return 0

    for r in rows:
        arch = RiskHistoryArchive(
            id=r.id,
            risk_id=r.risk_id,
            action=r.action,
            changed_by_id=r.changed_by_id,
            changed_at=r.changed_at,
            previous_values=r.previous_values,
            new_values=r.new_values,
            ip_address=r.ip_address,
            user_agent=r.user_agent,
            archived_at=datetime.now(timezone.utc),
        )
        db.add(arch)

    await db.execute(delete(RiskHistory).where(RiskHistory.changed_at < cutoff))
    await db.commit()
    return len(rows)
