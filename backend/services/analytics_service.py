"""Service layer for Analytics API."""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.risk import Department, Risk, RiskLink, RiskStatus
from schemas.analytics import (
    GraphEdge,
    GraphNode,
    HeatmapCell,
    InstitutionalDepartmentSummary,
    TrendPoint,
)


def _band_label_from_norm(norm: float) -> str:
    if norm >= 65:
        return "Critical"
    if norm >= 40:
        return "High"
    if norm >= 20:
        return "Medium"
    return "Low"


async def trend(db: AsyncSession, dept_id: Optional[UUID], days: int) -> List[TrendPoint]:
    days = max(1, min(int(days or 30), 365))
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)

    trend_timestamp = func.coalesce(Risk.updated_at, Risk.created_at)
    conditions = [trend_timestamp >= start]
    if dept_id:
        conditions.append(Risk.department_id == dept_id)

    # Avg of normalised score = risk_score / 6.25
    stmt = (
        select(func.date(trend_timestamp).label("day"), func.avg(Risk.risk_score / 6.25), func.count(Risk.id))
        .where(and_(*conditions))
        .group_by(func.date(trend_timestamp))
        .order_by(func.date(trend_timestamp).asc())
    )
    res = await db.execute(stmt)

    rows = {}
    for day_value, avg_value, count_value in res.all():
        key = day_value
        if isinstance(day_value, str):
            try:
                key = date.fromisoformat(day_value)
            except ValueError:
                key = None
        if key is None:
            continue
        rows[key] = (float(avg_value or 0.0), int(count_value or 0))

    # If no trend points exist in the range, use current portfolio average as baseline.
    if not rows:
        baseline_conditions = []
        if dept_id:
            baseline_conditions.append(Risk.department_id == dept_id)
        baseline_stmt = select(func.avg(Risk.risk_score / 6.25), func.count(Risk.id))
        if baseline_conditions:
            baseline_stmt = baseline_stmt.where(and_(*baseline_conditions))
        baseline_res = await db.execute(baseline_stmt)
        baseline_avg, baseline_cnt = baseline_res.one_or_none() or (0.0, 0)
        baseline = round(float(baseline_avg or 0.0), 1)
        cnt = int(baseline_cnt or 0)
        return [TrendPoint(day=(start.date() + timedelta(days=i)), avg_score=baseline, risk_count=cnt) for i in range(days)]

    out: List[TrendPoint] = []
    last_avg = 0.0
    last_cnt = 0
    for i in range(days):
        d = (start.date() + timedelta(days=i))
        if d in rows:
            avg, cnt = rows[d]
            last_avg, last_cnt = avg, cnt
        else:
            avg, cnt = last_avg, last_cnt
        out.append(TrendPoint(day=d, avg_score=round(avg, 1), risk_count=cnt))

    return out


async def heatmap(db: AsyncSession, dept_id: Optional[UUID]) -> List[HeatmapCell]:
    conditions = [Risk.status != RiskStatus.CLOSED]
    if dept_id:
        conditions.append(Risk.department_id == dept_id)

    stmt = (
        select(Risk.likelihood, Risk.impact, func.count(Risk.id))
        .where(and_(*conditions))
        .group_by(Risk.likelihood, Risk.impact)
        .order_by(Risk.likelihood.asc(), Risk.impact.asc())
    )
    res = await db.execute(stmt)
    return [HeatmapCell(likelihood=int(l), impact=int(i), count=int(c)) for l, i, c in res.all()]


async def institutional_summary(db: AsyncSession) -> Dict[str, object]:
    dep_res = await db.execute(select(Department).where(Department.is_active == True).order_by(Department.name))
    deps = dep_res.scalars().all()

    # Preload risk counts per dept
    risk_res = await db.execute(select(Risk.department_id, Risk.risk_score))
    rows = risk_res.all()

    by_dept: Dict[UUID, List[float]] = {}
    distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for dept_id, raw in rows:
        if dept_id is None or raw is None:
            continue
        by_dept.setdefault(dept_id, []).append(float(raw))
        band = _band_label_from_norm(float(raw) / 6.25)
        distribution[band] = distribution.get(band, 0) + 1

    dept_summaries: List[InstitutionalDepartmentSummary] = []

    for d in deps:
        scores = by_dept.get(d.id, [])
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for raw in scores:
            counts[_band_label_from_norm(raw / 6.25)] += 1

        iri_res = await db.execute(
            select(func.max(Risk.institutional_risk_index)).where(Risk.department_id == d.id)
        )
        iri = float(iri_res.scalar() or 0.0)

        dept_summaries.append(
            InstitutionalDepartmentSummary(
                department_id=d.id,
                department_name=d.name,
                iri=iri,
                total_risks=len(scores),
                critical=counts["Critical"],
                high=counts["High"],
                medium=counts["Medium"],
                low=counts["Low"],
            )
        )

    return {"departments": dept_summaries, "distribution": distribution}


async def risk_chain_graph(db: AsyncSession) -> Dict[str, object]:
    risks_res = await db.execute(select(Risk.id, Risk.title, Risk.department_id, Risk.risk_score))
    risks = risks_res.all()

    nodes = [
        GraphNode(
            id=str(rid),
            title=title,
            department_id=str(dept_id),
            normalised_score=round(float(raw or 1.0) / 6.25, 1),
        )
        for rid, title, dept_id, raw in risks
        if dept_id is not None
    ]

    links_res = await db.execute(select(RiskLink.source_risk_id, RiskLink.target_risk_id, RiskLink.weight, RiskLink.link_type))
    links = links_res.all()

    edges = [
        GraphEdge(
            source=str(src),
            target=str(tgt),
            weight=float(w),
            link_type=str(lt.value if hasattr(lt, "value") else lt),
        )
        for src, tgt, w, lt in links
    ]

    return {"nodes": nodes, "edges": edges}
