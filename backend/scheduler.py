"""
APScheduler registration for background ERM jobs.
"""

from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.forensic_engine import run_forensic_scan
from services.history_archive_service import archive_risk_history_older_than
from services.overdue_mitigation_alerts import create_overdue_mitigation_alerts
from services.scoring_service import recompute_all_scores


def register_scheduler(session_factory) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")

    async def forensic_scan_job():
        async with session_factory() as session:
            try:
                created = await run_forensic_scan(session)
                n = len(created)
                ts = datetime.now(timezone.utc).strftime("%H:%M")
                print(f"✅ Forensic scan complete — {n} new alerts raised at {ts}", flush=True)
            except Exception:
                await session.rollback()
                raise

    async def nightly_scores_job():
        async with session_factory() as session:
            try:
                updated = await recompute_all_scores(session)
                ts = datetime.now(timezone.utc).strftime("%H:%M")
                print(f"✅ IRI / score recomputation complete — {updated} risks updated at {ts}", flush=True)
            except Exception:
                await session.rollback()
                raise

    async def overdue_job():
        async with session_factory() as session:
            try:
                n = await create_overdue_mitigation_alerts(session)
                ts = datetime.now(timezone.utc).strftime("%H:%M")
                print(f"✅ Overdue mitigation check — {n} new alerts at {ts}", flush=True)
            except Exception:
                await session.rollback()
                raise

    async def archive_job():
        async with session_factory() as session:
            try:
                n = await archive_risk_history_older_than(session, years=2)
                ts = datetime.now(timezone.utc).strftime("%H:%M")
                print(f"✅ Risk history archive — {n} rows moved at {ts}", flush=True)
            except Exception:
                await session.rollback()
                raise

    scheduler.add_job(
        forensic_scan_job,
        trigger=IntervalTrigger(hours=6),
        id="forensic_scan",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        nightly_scores_job,
        trigger=CronTrigger(hour=23, minute=0),
        id="nightly_scores",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        overdue_job,
        trigger=IntervalTrigger(hours=1),
        id="overdue_mitigations",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        archive_job,
        trigger=IntervalTrigger(days=30),
        id="archive_risk_history",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    return scheduler
