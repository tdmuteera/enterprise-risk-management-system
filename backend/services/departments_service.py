"""Service layer for Departments API."""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.risk import Department, MitigationAction, MitigationStatus, Risk, RiskHistory, RiskLink, RiskStatus
from schemas.department import DepartmentCreate, DepartmentTrendEntry, DepartmentUpdate
from schemas.risk import ColourBand, RiskLinkSummary, RiskResponse
from services.domain_audit_service import log_domain_action
from services.recommendation_engine import get_recommendations_for_risk
from utils.risk_scorer import get_colour_band, normalise_score


def _colour_band_for_risk(risk: Risk) -> ColourBand:
    raw = float(risk.risk_score or 1.0)
    norm = normalise_score(raw)
    band = get_colour_band(norm)
    return ColourBand(label=band["label"], hex=band["hex"], tailwind=band["tailwind_class"])


async def _mitigation_counts(db: AsyncSession, risk_ids: List[UUID]) -> Tuple[Dict[UUID, int], Dict[UUID, int]]:
    if not risk_ids:
        return {}, {}

    total_stmt = (
        select(MitigationAction.risk_id, func.count(MitigationAction.id))
        .where(MitigationAction.risk_id.in_(risk_ids))
        .group_by(MitigationAction.risk_id)
    )
    total_res = await db.execute(total_stmt)
    total = {rid: int(cnt) for rid, cnt in total_res.all()}

    now = datetime.now(timezone.utc)
    overdue_stmt = (
        select(MitigationAction.risk_id, func.count(MitigationAction.id))
        .where(
            and_(
                MitigationAction.risk_id.in_(risk_ids),
                MitigationAction.due_date < now,
                MitigationAction.status != MitigationStatus.COMPLETED,
            )
        )
        .group_by(MitigationAction.risk_id)
    )
    overdue_res = await db.execute(overdue_stmt)
    overdue = {rid: int(cnt) for rid, cnt in overdue_res.all()}

    return total, overdue


async def _build_link_summaries(db: AsyncSession, risk_ids: List[UUID]) -> Dict[UUID, List[RiskLinkSummary]]:
    if not risk_ids:
        return {}

    stmt = (
        select(RiskLink)
        .where(or_(RiskLink.source_risk_id.in_(risk_ids), RiskLink.target_risk_id.in_(risk_ids)))
        .options(
            selectinload(RiskLink.source_risk).selectinload(Risk.department),
            selectinload(RiskLink.target_risk).selectinload(Risk.department),
        )
    )
    result = await db.execute(stmt)
    links = result.scalars().all()

    out: Dict[UUID, List[RiskLinkSummary]] = {rid: [] for rid in risk_ids}

    for link in links:
        src = link.source_risk
        tgt = link.target_risk
        if not src or not tgt:
            continue

        def _summary(other: Risk) -> RiskLinkSummary:
            other_raw = float(other.risk_score or 1.0)
            other_norm = normalise_score(other_raw)
            band = get_colour_band(other_norm)
            return RiskLinkSummary(
                linked_risk_id=other.id,
                title=other.title,
                department_id=other.department_id,
                department_name=other.department.name if other.department else None,
                link_type=str(link.link_type.value if hasattr(link.link_type, "value") else link.link_type),
                weight=float(link.weight),
                notes=link.notes,
                risk_score=other_raw,
                normalised_score=other_norm,
                colour_band=ColourBand(label=band["label"], hex=band["hex"], tailwind=band["tailwind_class"]),
            )

        if link.source_risk_id in out:
            out[link.source_risk_id].append(_summary(tgt))
        if link.target_risk_id in out:
            out[link.target_risk_id].append(_summary(src))

    return out


async def _to_risk_responses(db: AsyncSession, risks: List[Risk]) -> List[RiskResponse]:
    if not risks:
        return []

    risk_ids = [r.id for r in risks]
    links_map = await _build_link_summaries(db, risk_ids)
    total_map, overdue_map = await _mitigation_counts(db, risk_ids)

    out: List[RiskResponse] = []
    for r in risks:
        raw = float(r.risk_score or 1.0)
        norm = normalise_score(raw)
        band = get_colour_band(norm)

        out.append(
            RiskResponse(
                id=r.id,
                title=r.title,
                description=r.description,
                category=str(r.category.value if hasattr(r.category, "value") else r.category),
                department_id=r.department_id,
                owner_id=r.owner_id,
                likelihood=int(r.likelihood),
                impact=int(r.impact),
                velocity=int(r.velocity),
                detectability=int(r.detectability),
                risk_score=raw,
                normalised_score=norm,
                colour_band=ColourBand(label=band["label"], hex=band["hex"], tailwind=band["tailwind_class"]),
                status=str(r.status.value if hasattr(r.status, "value") else r.status),
                iri=float(r.institutional_risk_index) if r.institutional_risk_index is not None else None,
                created_at=r.created_at,
                updated_at=r.updated_at,
                recommendations=get_recommendations_for_risk(r),
                linked_risks=links_map.get(r.id, []),
                mitigation_count=total_map.get(r.id, 0),
                overdue_mitigations=overdue_map.get(r.id, 0),
            )
        )

    return out


async def list_active_departments(db: AsyncSession) -> List[Department]:
    result = await db.execute(select(Department).where(Department.is_active == True).order_by(Department.name))
    return result.scalars().all()


async def create_department(
    db: AsyncSession,
    payload: DepartmentCreate,
    user_id: UUID,
    request=None,
) -> Department:
    dept = Department(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        head_of_dept=payload.head_of_dept,
        is_active=True,
    )
    db.add(dept)
    await db.flush()

    await log_domain_action(
        db,
        entity_type="department",
        entity_id=dept.id,
        user_id=user_id,
        action="created",
        previous_values={},
        new_values={
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "head_of_dept": dept.head_of_dept,
            "is_active": dept.is_active,
        },
        request=request,
    )

    await db.commit()
    await db.refresh(dept)
    return dept


async def get_department(db: AsyncSession, dept_id: UUID) -> Optional[Department]:
    result = await db.execute(select(Department).where(Department.id == dept_id))
    return result.scalar_one_or_none()


async def get_department_open_risk_count(db: AsyncSession, dept_id: UUID) -> int:
    stmt = select(func.count(Risk.id)).where(
        and_(Risk.department_id == dept_id, Risk.status != RiskStatus.CLOSED)
    )
    res = await db.execute(stmt)
    return int(res.scalar() or 0)


async def get_department_iri(db: AsyncSession, dept_id: UUID) -> float:
    stmt = select(func.max(Risk.institutional_risk_index)).where(Risk.department_id == dept_id)
    res = await db.execute(stmt)
    val = res.scalar()
    return float(val or 0.0)


async def update_department(
    db: AsyncSession,
    dept: Department,
    payload: DepartmentUpdate,
    user_id: UUID,
    request=None,
) -> Department:
    previous = {
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "head_of_dept": dept.head_of_dept,
        "is_active": dept.is_active,
    }

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(dept, k, v)

    await log_domain_action(
        db,
        entity_type="department",
        entity_id=dept.id,
        user_id=user_id,
        action="updated",
        previous_values=previous,
        new_values={
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "head_of_dept": dept.head_of_dept,
            "is_active": dept.is_active,
        },
        request=request,
    )

    await db.commit()
    await db.refresh(dept)
    return dept


async def get_department_risks(
    db: AsyncSession,
    dept_id: UUID,
    page: int,
    page_size: int,
) -> Tuple[List[RiskResponse], int, List[RiskResponse]]:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20

    where_clause = and_(Risk.department_id == dept_id, Risk.status != RiskStatus.CLOSED)

    total_stmt = select(func.count(Risk.id)).where(where_clause)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    stmt = (
        select(Risk)
        .where(where_clause)
        .order_by(Risk.risk_score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    res = await db.execute(stmt)
    risks = res.scalars().all()

    top_stmt = select(Risk).where(where_clause).order_by(Risk.risk_score.desc()).limit(5)
    top_res = await db.execute(top_stmt)
    top = top_res.scalars().all()

    return await _to_risk_responses(db, risks), total, await _to_risk_responses(db, top)


async def get_department_summary(
    db: AsyncSession,
    dept_id: UUID,
) -> Tuple[int, Dict[str, int], List[RiskResponse], float, List[DepartmentTrendEntry]]:
    # total risks (all statuses)
    total_stmt = select(func.count(Risk.id)).where(Risk.department_id == dept_id)
    total_res = await db.execute(total_stmt)
    total = int(total_res.scalar() or 0)

    # distribution by band (based on risk_score)
    stmt = select(Risk.risk_score).where(Risk.department_id == dept_id)
    res = await db.execute(stmt)
    scores = [float(x[0]) for x in res.all() if x[0] is not None]

    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for raw in scores:
        band = get_colour_band(normalise_score(raw))["label"]
        counts[band] = counts.get(band, 0) + 1

    # top5
    top_stmt = select(Risk).where(Risk.department_id == dept_id).order_by(Risk.risk_score.desc()).limit(5)
    top_res = await db.execute(top_stmt)
    top = top_res.scalars().all()
    top5 = await _to_risk_responses(db, top)

    iri = await get_department_iri(db, dept_id)

    # Trend: last 7 days based on immutable RiskHistory for risks in this dept
    start = datetime.now(timezone.utc) - timedelta(days=6)
    hist_stmt = (
        select(RiskHistory.action, RiskHistory.changed_at, RiskHistory.new_values)
        .join(Risk, Risk.id == RiskHistory.risk_id)
        .where(and_(Risk.department_id == dept_id, RiskHistory.changed_at >= start))
        .order_by(RiskHistory.changed_at.asc())
    )
    hist_res = await db.execute(hist_stmt)
    rows = hist_res.all()

    by_day: Dict[date, DepartmentTrendEntry] = {}
    for i in range(7):
        d = (start.date() + timedelta(days=i))
        by_day[d] = DepartmentTrendEntry(day=d, created=0, updated=0, closed=0)

    for action, changed_at, new_values in rows:
        d = changed_at.date()
        if d not in by_day:
            continue
        a = str(action.value if hasattr(action, "value") else action)
        if a == "created":
            by_day[d].created += 1
        else:
            by_day[d].updated += 1

        if isinstance(new_values, dict) and new_values.get("status") == "Closed":
            by_day[d].closed += 1

    trend = [by_day[k] for k in sorted(by_day.keys())]

    return total, counts, top5, iri, trend
