"""Risk CRUD API.

Implements:
- Full CRUD + filtering/pagination
- Role checks + department scoping
- Risk scoring (raw + normalised + colour bands)
- Immutable audit trail entries
- Background forensic checks (run_forensic_scan)
- Cross-department risk linking + IRI recomputation
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status as http_status
from fastapi.responses import Response
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.dependencies import get_current_user, get_dept_user, require_roles, DEPT_BOUND_ROLES
from models.alert import AlertRole, AlertSeverity, AlertType
from models.risk import (
    Alert,
    Department,
    MitigationAction,
    MitigationStatus,
    Risk,
    RiskCategory,
    RiskHistory,
    RiskLink,
    RiskLinkType,
    RiskStatus,
    RiskType,
    User,
)
from schemas.risk import (
    ColourBand,
    ReviewJustification,
    RiskCreate,
    RiskDetailResponse,
    RiskHistoryEntry,
    RiskLinkCreate,
    RiskLinkSummary,
    RiskListResponse,
    RiskResponse,
    RiskUpdate,
    UserSummary,
)
from services.audit_service import export_audit_log_to_excel, log_action
from services.forensic_engine import run_forensic_scan
from services.recommendation_engine import get_recommendations_for_risk
from utils.db_dep import get_db
from utils.risk_scorer import calculate_iri, calculate_risk_score, detect_risk_chain, get_colour_band, normalise_score

router = APIRouter(prefix="/api/v1/risks", tags=["Risks"])

DEPT_SCOPED_ROLES = {"dept_user", "data_clerk", "risk_clerk"}

# Who may create / link risks (includes managers and department heads).
ROLE_CREATE_RISK = (
    "dept_user",
    "data_clerk",
    "risk_clerk",
    "risk_officer",
    "risk_manager",
    "department_head",
    "admin",
)
# Approve, reject, delete soft paths, forensic exports, institutional chains, etc.
ROLE_RISK_SUPERVISOR = ("risk_officer", "risk_manager", "department_head", "admin")

DEPARTMENT_DEFAULT_CATEGORY = {
    "FIN": RiskCategory.FINANCIAL,
    "HR": RiskCategory.HR,
    "ACAD": RiskCategory.ACADEMIC,
    "IT": RiskCategory.IT,
    "SA": RiskCategory.OPERATIONAL,
    "ENG": RiskCategory.OPERATIONAL,
    "AHS": RiskCategory.OPERATIONAL,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def _client_meta(request: Request) -> Tuple[Optional[str], Optional[str]]:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        ip = xff.split(",")[0].strip() or None
    else:
        ip = request.client.host if request.client else None
    return ip, request.headers.get("user-agent")


async def _department_mapped_category(db: AsyncSession, department_id: UUID) -> Optional[RiskCategory]:
    result = await db.execute(select(Department).where(Department.id == department_id))
    dept = result.scalar_one_or_none()
    if not dept:
        return None
    code = (dept.code or "").upper()
    if code in DEPARTMENT_DEFAULT_CATEGORY:
        return DEPARTMENT_DEFAULT_CATEGORY[code]
    name = (dept.name or "").lower()
    if "finance" in name:
        return RiskCategory.FINANCIAL
    if "human" in name:
        return RiskCategory.HR
    if "academic" in name:
        return RiskCategory.ACADEMIC
    if "information technology" in name or name == "it":
        return RiskCategory.IT
    return RiskCategory.OPERATIONAL


def _colour_band_for_risk(risk: Risk) -> ColourBand:
    raw = float(risk.risk_score or 1.0)
    norm = normalise_score(raw)
    band = get_colour_band(norm)
    return ColourBand(label=band["label"], hex=band["hex"], tailwind=band["tailwind_class"])


def _normalised_score_for_risk(risk: Risk) -> float:
    raw = float(risk.risk_score or 1.0)
    return normalise_score(raw)


def _risk_category(value: str) -> RiskCategory:
    try:
        return RiskCategory(value)
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid category: {value}")


def _risk_status(value: str) -> RiskStatus:
    try:
        return RiskStatus(value)
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid status: {value}")


def _raw_score_bounds_for_colour(label: str) -> Tuple[Optional[float], Optional[float]]:
    l = (label or "").strip().lower()
    # thresholds are expressed in NORMALISED score; raw = normalised * 6.25
    if l == "critical":
        return 65 * 6.25, None
    if l == "high":
        return 40 * 6.25, (65 * 6.25) - 1e-9
    if l == "medium":
        return 20 * 6.25, (40 * 6.25) - 1e-9
    if l == "low":
        return None, (20 * 6.25) - 1e-9
    raise HTTPException(status_code=422, detail=f"Invalid colour_band: {label}")


async def _run_forensic_scan(session_factory) -> None:
    async with session_factory() as session:
        try:
            await run_forensic_scan(session)
        except Exception:
            await session.rollback()


async def _recompute_cluster_iri(db: AsyncSession, root_ids: Iterable[UUID]) -> Set[UUID]:
    """Recompute IRI for the connected component containing any root_ids.

    Returns the set of risk IDs updated.
    """
    root_strs = {str(rid) for rid in root_ids}

    risks_result = await db.execute(select(Risk.id, Risk.department_id, Risk.risk_score, Risk.likelihood, Risk.impact, Risk.velocity, Risk.detectability))
    risks_rows = risks_result.all()
    if not risks_rows:
        return set()

    links_result = await db.execute(select(RiskLink.source_risk_id, RiskLink.target_risk_id, RiskLink.weight))
    links_rows = links_result.all()

    risks_dict = [{"id": str(r[0])} for r in risks_rows]
    links_dict = [{"source_risk_id": str(l[0]), "target_risk_id": str(l[1]), "weight": float(l[2])} for l in links_rows]

    clusters = detect_risk_chain(risks_dict, links_dict)
    cluster_ids: Optional[List[UUID]] = None

    for cluster in clusters:
        if any(rid in root_strs for rid in cluster):
            cluster_ids = [UUID(rid) for rid in cluster]
            break

    if not cluster_ids:
        return set()

    cluster_set = set(cluster_ids)

    # Load actual Risk objects for update
    cluster_risks_result = await db.execute(select(Risk).where(Risk.id.in_(cluster_ids)))
    cluster_risks = cluster_risks_result.scalars().all()
    by_id: Dict[UUID, Risk] = {r.id: r for r in cluster_risks}

    cluster_depts = {r.department_id for r in cluster_risks if r.department_id}
    dept_count = max(1, len(cluster_depts))

    # Build adjacency from links_rows
    adjacency: Dict[UUID, List[Tuple[UUID, float]]] = {rid: [] for rid in cluster_set}
    for src_id, tgt_id, weight in links_rows:
        if src_id in cluster_set and tgt_id in cluster_set:
            adjacency[src_id].append((tgt_id, float(weight)))
            adjacency[tgt_id].append((src_id, float(weight)))

    updated: Set[UUID] = set()

    for rid in cluster_set:
        risk = by_id.get(rid)
        if not risk:
            continue

        linked_scores: List[float] = []
        weights: List[float] = []

        for other_id, w in adjacency.get(rid, []):
            other = by_id.get(other_id)
            if not other:
                continue
            raw_other = float(other.risk_score or calculate_risk_score(other.likelihood, other.impact, other.velocity, other.detectability))
            linked_scores.append(normalise_score(raw_other))
            weights.append(float(w))

        risk.institutional_risk_index = calculate_iri(linked_scores, weights, dept_count) if linked_scores else 0.0
        updated.add(rid)

    return updated


async def _build_link_summaries(
    db: AsyncSession,
    risk_ids: List[UUID],
) -> Dict[UUID, List[RiskLinkSummary]]:
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

        def _summary(for_risk_id: UUID, other: Risk) -> RiskLinkSummary:
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
            out[link.source_risk_id].append(_summary(link.source_risk_id, tgt))
        if link.target_risk_id in out:
            out[link.target_risk_id].append(_summary(link.target_risk_id, src))

    return out


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
        .where(MitigationAction.risk_id.in_(risk_ids))
        .where(MitigationAction.due_date < now)
        .where(MitigationAction.status != MitigationStatus.COMPLETED)
        .group_by(MitigationAction.risk_id)
    )
    overdue_res = await db.execute(overdue_stmt)
    overdue = {rid: int(cnt) for rid, cnt in overdue_res.all()}

    return total, overdue


def _risk_to_response(
    risk: Risk,
    linked: List[RiskLinkSummary],
    mitigation_count: int,
    overdue_mitigations: int,
) -> RiskResponse:
    raw = float(risk.risk_score or calculate_risk_score(risk.likelihood, risk.impact, risk.velocity, risk.detectability))
    norm = normalise_score(raw)
    band = get_colour_band(norm)

    return RiskResponse(
        id=risk.id,
        title=risk.title,
        description=risk.description,
        category=str(risk.category.value if hasattr(risk.category, "value") else risk.category),
        department_id=risk.department_id,
        owner_id=risk.owner_id,
        likelihood=risk.likelihood,
        impact=risk.impact,
        velocity=risk.velocity,
        detectability=risk.detectability,
        risk_score=raw,
        normalised_score=norm,
        colour_band=ColourBand(label=band["label"], hex=band["hex"], tailwind=band["tailwind_class"]),
        status=str(risk.status.value if hasattr(risk.status, "value") else risk.status),
        risk_type=str(risk.risk_type.value if hasattr(risk.risk_type, "value") else risk.risk_type) if risk.risk_type else None,
        parent_risk_id=risk.parent_risk_id,
        reviewer_id=risk.reviewer_id,
        review_justification=risk.review_justification,
        reviewed_at=risk.reviewed_at,
        iri=risk.institutional_risk_index,
        created_at=risk.created_at,
        updated_at=risk.updated_at,
        recommendations=get_recommendations_for_risk(risk),
        linked_risks=linked,
        mitigation_count=mitigation_count,
        overdue_mitigations=overdue_mitigations,
    )


def _ensure_dept_scope_for_read(current_user: User, risk: Risk) -> None:
    if _role(current_user) in DEPT_BOUND_ROLES:
        get_dept_user(current_user, risk)


def _assert_department_head_same_dept(current_user: User, risk: Risk) -> None:
    """Department heads may only approve/reject risks in their own department."""
    if _role(current_user) != "department_head":
        return
    if not current_user.department_id or risk.department_id != current_user.department_id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Department heads can only review risks in their department",
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=RiskListResponse)
async def list_risks(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    department_id: Optional[UUID] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    colour_band: Optional[str] = None,
    sort_by: str = "score",
    order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> RiskListResponse:
    role = _role(current_user)

    if page < 1:
        raise HTTPException(status_code=422, detail="page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=422, detail="page_size must be 1-100")

    effective_dept = department_id
    if _role(current_user) in DEPT_BOUND_ROLES:
        if not current_user.department_id:
            raise HTTPException(status_code=403, detail="This role must belong to a department to list risks")
        effective_dept = current_user.department_id

    conditions = []
    if effective_dept is not None:
        conditions.append(Risk.department_id == effective_dept)
    if category is not None:
        conditions.append(Risk.category == _risk_category(category))
    if status is not None:
        conditions.append(Risk.status == _risk_status(status))
    if colour_band is not None:
        lo, hi = _raw_score_bounds_for_colour(colour_band)
        if lo is not None:
            conditions.append(Risk.risk_score >= lo)
        if hi is not None:
            conditions.append(Risk.risk_score <= hi)

    where_clause = and_(*conditions) if conditions else None

    sort_map = {
        "score": Risk.risk_score,
        "created_at": Risk.created_at,
        "updated_at": Risk.updated_at,
    }
    if sort_by not in sort_map:
        raise HTTPException(status_code=422, detail="sort_by must be one of: score|created_at|updated_at")

    order_fn = desc if order.lower() == "desc" else asc if order.lower() == "asc" else None
    if order_fn is None:
        raise HTTPException(status_code=422, detail="order must be asc|desc")

    base_stmt = select(Risk)
    if where_clause is not None:
        base_stmt = base_stmt.where(where_clause)

    count_stmt = select(func.count()).select_from(Risk)
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)

    total = int((await db.execute(count_stmt)).scalar_one())

    stmt = base_stmt.order_by(order_fn(sort_map[sort_by])).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    top5_stmt = base_stmt.order_by(desc(Risk.risk_score)).limit(5)
    top5_result = await db.execute(top5_stmt)
    top5 = top5_result.scalars().all()

    all_ids = list({r.id for r in items + top5})
    links_map = await _build_link_summaries(db, all_ids)
    mit_counts, overdue_counts = await _mitigation_counts(db, all_ids)

    def _mk(r: Risk) -> RiskResponse:
        return _risk_to_response(
            r,
            linked=links_map.get(r.id, []),
            mitigation_count=mit_counts.get(r.id, 0),
            overdue_mitigations=overdue_counts.get(r.id, 0),
        )

    return RiskListResponse(
        items=[_mk(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        top_5=[_mk(r) for r in top5],
    )


@router.post(
    "",
    response_model=RiskResponse,
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(*ROLE_CREATE_RISK))],
)
async def create_risk(
    payload: RiskCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskResponse:
    role = _role(current_user)

    if role in DEPT_SCOPED_ROLES or role == "department_head":
        if not current_user.department_id:
            raise HTTPException(status_code=403, detail="This role must belong to a department")
        department_id = current_user.department_id
        owner_id = current_user.id
        category_enum = await _department_mapped_category(db, department_id)
        if category_enum is None:
            raise HTTPException(status_code=422, detail="Invalid department for current user")
    else:
        category_enum = _risk_category(payload.category)
        if payload.department_id is None or payload.owner_id is None:
            raise HTTPException(status_code=422, detail="department_id and owner_id are required")
        department_id = payload.department_id
        owner_id = payload.owner_id

    raw_score = calculate_risk_score(payload.likelihood, payload.impact, payload.velocity, payload.detectability)
    norm_score = normalise_score(raw_score)

    # Determine initial status based on role
    if role in DEPT_SCOPED_ROLES or role == "department_head":
        initial_status = RiskStatus.PENDING_APPROVAL
    else:
        initial_status = RiskStatus.OPEN

    # Determine risk_type
    risk_type_enum = RiskType.INHERENT
    if payload.risk_type:
        try:
            risk_type_enum = RiskType(payload.risk_type)
        except (ValueError, KeyError):
            raise HTTPException(status_code=422, detail=f"Invalid risk_type: {payload.risk_type}")

    risk = Risk(
        title=payload.title,
        description=payload.description,
        category=category_enum,
        department_id=department_id,
        owner_id=owner_id,
        likelihood=payload.likelihood,
        impact=payload.impact,
        velocity=payload.velocity,
        detectability=payload.detectability,
        risk_score=raw_score,
        status=initial_status,
        risk_type=risk_type_enum,
        parent_risk_id=payload.parent_risk_id,
    )

    ip, ua = _client_meta(request)

    try:
        db.add(risk)
        await db.flush()

        await log_action(
            db=db,
            risk_id=risk.id,
            user_id=current_user.id,
            action="created",
            previous_values={},
            new_values={
                "title": risk.title,
                "description": risk.description,
                "category": str(risk.category.value),
                "department_id": str(risk.department_id),
                "owner_id": str(risk.owner_id),
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "velocity": risk.velocity,
                "detectability": risk.detectability,
                "risk_score": float(risk.risk_score),
                "status": str(risk.status.value),
            },
            request=request,
        )

        # Auto alert + escalation if Critical
        if norm_score >= 65:
            alert = Alert(
                alert_type=AlertType.HIGH_RISK,
                risk_id=risk.id,
                message=f"CRITICAL: Risk '{risk.title}' created with critical score ({norm_score})",
                severity=AlertSeverity.CRITICAL,
                is_read=False,
                is_dismissed=False,
                created_for_role=AlertRole.RISK_OFFICER,
            )
            db.add(alert)

        await db.commit()
        await db.refresh(risk)

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    # Forensic checks in background
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory:
        background_tasks.add_task(_run_forensic_scan, session_factory)

    links_map = await _build_link_summaries(db, [risk.id])
    mit_counts, overdue_counts = await _mitigation_counts(db, [risk.id])

    return _risk_to_response(
        risk,
        linked=links_map.get(risk.id, []),
        mitigation_count=mit_counts.get(risk.id, 0),
        overdue_mitigations=overdue_counts.get(risk.id, 0),
    )


@router.get("/pending", response_model=List[RiskResponse], dependencies=[Depends(require_roles(*ROLE_RISK_SUPERVISOR))])
async def list_pending_risks_route(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RiskResponse]:
    """List all risks with status PENDING_APPROVAL for review."""
    stmt = select(Risk).where(Risk.status == RiskStatus.PENDING_APPROVAL)
    if _role(current_user) == "department_head":
        if not current_user.department_id:
            raise HTTPException(status_code=403, detail="Department heads must belong to a department")
        stmt = stmt.where(Risk.department_id == current_user.department_id)
    stmt = stmt.order_by(desc(Risk.created_at))
    result = await db.execute(stmt)
    risks = result.scalars().all()

    ids = [r.id for r in risks]
    links_map = await _build_link_summaries(db, ids)
    mit_counts, overdue_counts = await _mitigation_counts(db, ids)

    return [
        _risk_to_response(r, links_map.get(r.id, []), mit_counts.get(r.id, 0), overdue_counts.get(r.id, 0))
        for r in risks
    ]


@router.get("/{risk_id}", response_model=RiskDetailResponse)
async def get_risk(
    risk_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskDetailResponse:
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    _ensure_dept_scope_for_read(current_user, risk)

    links_map = await _build_link_summaries(db, [risk.id])
    mit_counts, overdue_counts = await _mitigation_counts(db, [risk.id])

    history_stmt = (
        select(RiskHistory)
        .where(RiskHistory.risk_id == risk_id)
        .order_by(desc(RiskHistory.changed_at))
        .options(selectinload(RiskHistory.changed_by))
    )
    history_res = await db.execute(history_stmt)
    history = history_res.scalars().all()

    audit_trail: List[RiskHistoryEntry] = []
    for h in history:
        u = h.changed_by
        audit_trail.append(
            RiskHistoryEntry(
                id=h.id,
                risk_id=h.risk_id,
                action=str(h.action.value if hasattr(h.action, "value") else h.action),
                changed_at=h.changed_at,
                ip_address=h.ip_address,
                user_agent=h.user_agent,
                previous_values=h.previous_values or {},
                new_values=h.new_values or {},
                user=(
                    UserSummary(
                        id=u.id,
                        email=u.email,
                        full_name=u.full_name,
                        role=_role(u),
                        department_id=u.department_id,
                    )
                    if u
                    else None
                ),
            )
        )

    base = _risk_to_response(
        risk,
        linked=links_map.get(risk.id, []),
        mitigation_count=mit_counts.get(risk.id, 0),
        overdue_mitigations=overdue_counts.get(risk.id, 0),
    )

    await log_action(
        db=db,
        risk_id=risk.id,
        user_id=current_user.id,
        action="viewed",
        previous_values={},
        new_values={},
        request=request,
    )
    await db.commit()

    return RiskDetailResponse(**base.model_dump(), audit_trail=audit_trail)


@router.patch(
    "/{risk_id}",
    response_model=RiskResponse,
    dependencies=[Depends(require_roles(*ROLE_CREATE_RISK))],
)
async def patch_risk(
    risk_id: UUID,
    payload: RiskUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskResponse:
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    _ensure_dept_scope_for_read(current_user, risk)

    role = _role(current_user)

    # Role-based edit restrictions
    if role in DEPT_SCOPED_ROLES:
        # dept_user can only edit risks they own AND only when status is DRAFT or REJECTED
        if risk.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="dept_user can only edit risks they own")
        risk_status_val = risk.status.value if hasattr(risk.status, "value") else str(risk.status)
        if risk_status_val not in ("Draft", "Rejected", "Pending Approval"):
            raise HTTPException(
                status_code=403,
                detail="dept_user can only edit risks in Draft, Rejected, or Pending Approval status",
            )
    elif role in {"risk_officer", "risk_manager", "department_head"}:
        # Supervisors may edit risks in their scope (department heads are already department-scoped above).
        pass

    if role in DEPT_SCOPED_ROLES and (payload.department_id is not None or payload.owner_id is not None):
        raise HTTPException(status_code=403, detail="department-scoped users cannot reassign department/owner")
    if role == "department_head" and payload.department_id is not None:
        if not current_user.department_id or payload.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="Department heads cannot move risks to another department",
            )
    if role in DEPT_SCOPED_ROLES and payload.category is not None:
        enforced_category = await _department_mapped_category(db, risk.department_id)
        if enforced_category is None:
            raise HTTPException(status_code=422, detail="Invalid department mapping")
        risk.category = enforced_category

    before: Dict[str, Any] = {
        "title": risk.title,
        "description": risk.description,
        "category": str(risk.category.value if hasattr(risk.category, "value") else risk.category),
        "department_id": str(risk.department_id),
        "owner_id": str(risk.owner_id),
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "velocity": risk.velocity,
        "detectability": risk.detectability,
        "risk_score": float(risk.risk_score or 1.0),
        "status": str(risk.status.value if hasattr(risk.status, "value") else risk.status),
        "institutional_risk_index": float(risk.institutional_risk_index or 0.0),
    }

    # Apply partial updates
    if payload.title is not None:
        risk.title = payload.title
    if payload.description is not None:
        risk.description = payload.description
    if payload.category is not None and role not in DEPT_SCOPED_ROLES:
        risk.category = _risk_category(payload.category)
    if payload.department_id is not None:
        risk.department_id = payload.department_id
    if payload.owner_id is not None:
        risk.owner_id = payload.owner_id

    factors_changed = False
    for f in ("likelihood", "impact", "velocity", "detectability"):
        v = getattr(payload, f)
        if v is not None:
            setattr(risk, f, v)
            factors_changed = True

    status_changed = False
    if payload.status is not None:
        new_status = _risk_status(payload.status)
        status_changed = risk.status != new_status
        risk.status = new_status

    old_raw = float(risk.risk_score or 1.0)
    score_changed = False
    if factors_changed:
        new_raw = calculate_risk_score(risk.likelihood, risk.impact, risk.velocity, risk.detectability)
        score_changed = float(risk.risk_score or 0.0) != float(new_raw)
        risk.risk_score = new_raw

    # If score changed, recompute IRI for cluster (and include it in audit diff)
    if score_changed:
        await _recompute_cluster_iri(db, [risk.id])

    after: Dict[str, Any] = {
        "title": risk.title,
        "description": risk.description,
        "category": str(risk.category.value if hasattr(risk.category, "value") else risk.category),
        "department_id": str(risk.department_id),
        "owner_id": str(risk.owner_id),
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "velocity": risk.velocity,
        "detectability": risk.detectability,
        "risk_score": float(risk.risk_score or 1.0),
        "status": str(risk.status.value if hasattr(risk.status, "value") else risk.status),
        "institutional_risk_index": float(risk.institutional_risk_index or 0.0),
    }

    action = "status_changed" if status_changed else "updated"
    if score_changed and not status_changed:
        action = "score_changed"

    try:
        await log_action(
            db=db,
            risk_id=risk.id,
            user_id=current_user.id,
            action=action,
            previous_values=before,
            new_values=after,
            request=request,
        )

        await db.commit()
        await db.refresh(risk)

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    # Forensic checks in background (score suppression specifically after score change)
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory:
        background_tasks.add_task(_run_forensic_scan, session_factory)

    links_map = await _build_link_summaries(db, [risk.id])
    mit_counts, overdue_counts = await _mitigation_counts(db, [risk.id])

    return _risk_to_response(
        risk,
        linked=links_map.get(risk.id, []),
        mitigation_count=mit_counts.get(risk.id, 0),
        overdue_mitigations=overdue_counts.get(risk.id, 0),
    )


@router.delete(
    "/{risk_id}",
    dependencies=[Depends(require_roles(*ROLE_RISK_SUPERVISOR))],
)
async def delete_risk(
    risk_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    # Dept scoping only applies for dept_user (who can't hit this endpoint anyway)
    _ensure_dept_scope_for_read(current_user, risk)

    # Call scoring engine (for critical-check semantics)
    raw_before = float(risk.risk_score or calculate_risk_score(risk.likelihood, risk.impact, risk.velocity, risk.detectability))
    norm_before = normalise_score(raw_before)

    before = {"status": str(risk.status.value if hasattr(risk.status, "value") else risk.status), "risk_score": raw_before}

    risk.status = RiskStatus.CLOSED

    after = {"status": str(risk.status.value if hasattr(risk.status, "value") else risk.status), "risk_score": raw_before}

    try:
        await log_action(
            db=db,
            risk_id=risk.id,
            user_id=current_user.id,
            action="deleted",
            previous_values=before,
            new_values=after,
            request=request,
        )
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    # Forensic checks in background (sudden disappearance when critical)
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory:
        background_tasks.add_task(_run_forensic_scan, session_factory)

    return {"status": "ok"}


@router.post(
    "/{risk_id}/approve",
    response_model=RiskResponse,
    dependencies=[Depends(require_roles(*ROLE_RISK_SUPERVISOR))],
)
async def approve_risk(
    risk_id: UUID,
    payload: ReviewJustification,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskResponse:
    """Approve a risk that is in PENDING_APPROVAL status."""
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    _assert_department_head_same_dept(current_user, risk)

    risk_status_val = risk.status.value if hasattr(risk.status, "value") else str(risk.status)
    if risk_status_val != "Pending Approval":
        raise HTTPException(status_code=400, detail="Risk is not in Pending Approval status")

    before_status = risk_status_val
    risk.status = RiskStatus.APPROVED
    risk.reviewer_id = current_user.id
    risk.review_justification = payload.justification
    risk.reviewed_at = datetime.now(timezone.utc)

    try:
        await log_action(
            db=db,
            risk_id=risk.id,
            user_id=current_user.id,
            action="status_changed",
            previous_values={"status": before_status},
            new_values={"status": "Approved", "reviewer_id": str(current_user.id), "review_justification": payload.justification},
            request=request,
        )
        await db.commit()
        await db.refresh(risk)
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    links_map = await _build_link_summaries(db, [risk.id])
    mit_counts, overdue_counts = await _mitigation_counts(db, [risk.id])

    return _risk_to_response(
        risk,
        linked=links_map.get(risk.id, []),
        mitigation_count=mit_counts.get(risk.id, 0),
        overdue_mitigations=overdue_counts.get(risk.id, 0),
    )


@router.post(
    "/{risk_id}/reject",
    response_model=RiskResponse,
    dependencies=[Depends(require_roles(*ROLE_RISK_SUPERVISOR))],
)
async def reject_risk(
    risk_id: UUID,
    payload: ReviewJustification,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskResponse:
    """Reject a risk that is in PENDING_APPROVAL status."""
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    _assert_department_head_same_dept(current_user, risk)

    risk_status_val = risk.status.value if hasattr(risk.status, "value") else str(risk.status)
    if risk_status_val != "Pending Approval":
        raise HTTPException(status_code=400, detail="Risk is not in Pending Approval status")

    before_status = risk_status_val
    risk.status = RiskStatus.REJECTED
    risk.reviewer_id = current_user.id
    risk.review_justification = payload.justification
    risk.reviewed_at = datetime.now(timezone.utc)

    try:
        await log_action(
            db=db,
            risk_id=risk.id,
            user_id=current_user.id,
            action="status_changed",
            previous_values={"status": before_status},
            new_values={"status": "Rejected", "reviewer_id": str(current_user.id), "review_justification": payload.justification},
            request=request,
        )
        await db.commit()
        await db.refresh(risk)
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    links_map = await _build_link_summaries(db, [risk.id])
    mit_counts, overdue_counts = await _mitigation_counts(db, [risk.id])

    return _risk_to_response(
        risk,
        linked=links_map.get(risk.id, []),
        mitigation_count=mit_counts.get(risk.id, 0),
        overdue_mitigations=overdue_counts.get(risk.id, 0),
    )


@router.get("/{risk_id}/history", response_model=List[RiskHistoryEntry])
async def risk_history(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 500,
    offset: int = 0,
) -> List[RiskHistoryEntry]:
    risk_res = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = risk_res.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    _ensure_dept_scope_for_read(current_user, risk)

    stmt = (
        select(RiskHistory)
        .where(RiskHistory.risk_id == risk_id)
        .order_by(desc(RiskHistory.changed_at))
        .limit(limit)
        .offset(offset)
        .options(selectinload(RiskHistory.changed_by))
    )
    res = await db.execute(stmt)
    entries = res.scalars().all()

    out: List[RiskHistoryEntry] = []
    for e in entries:
        u = e.changed_by
        out.append(
            RiskHistoryEntry(
                id=e.id,
                risk_id=e.risk_id,
                action=str(e.action.value if hasattr(e.action, "value") else e.action),
                changed_at=e.changed_at,
                ip_address=e.ip_address,
                user_agent=e.user_agent,
                previous_values=e.previous_values or {},
                new_values=e.new_values or {},
                user=(
                    UserSummary(
                        id=u.id,
                        email=u.email,
                        full_name=u.full_name,
                        role=_role(u),
                        department_id=u.department_id,
                    )
                    if u
                    else None
                ),
            )
        )

    return out


@router.get("/{risk_id}/recommendations", response_model=List[str])
async def risk_recommendations(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[str]:
    res = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = res.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    _ensure_dept_scope_for_read(current_user, risk)
    return get_recommendations_for_risk(risk)


@router.post(
    "/{risk_id}/link",
    response_model=RiskResponse,
    dependencies=[Depends(require_roles(*ROLE_CREATE_RISK))],
)
async def link_risk(
    risk_id: UUID,
    payload: RiskLinkCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskResponse:
    if payload.target_risk_id == risk_id:
        raise HTTPException(status_code=422, detail="target_risk_id must be different from source")

    source_res = await db.execute(select(Risk).where(Risk.id == risk_id))
    source = source_res.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")

    get_dept_user(current_user, source)

    target_res = await db.execute(select(Risk).where(Risk.id == payload.target_risk_id))
    target = target_res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail=f"Risk {payload.target_risk_id} not found")

    if source.department_id == target.department_id:
        raise HTTPException(status_code=422, detail="Source and target risks must be in different departments")

    try:
        link_type = RiskLinkType(payload.link_type)
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid link_type: {payload.link_type}")

    before_source = {"institutional_risk_index": float(source.institutional_risk_index or 0.0)}
    before_target = {"institutional_risk_index": float(target.institutional_risk_index or 0.0)}

    link = RiskLink(
        source_risk_id=source.id,
        target_risk_id=target.id,
        link_type=link_type,
        weight=float(payload.weight),
        notes=payload.notes,
        created_by_id=current_user.id,
    )

    try:
        db.add(link)
        await db.flush()

        await _recompute_cluster_iri(db, [source.id, target.id])

        after_source = {"institutional_risk_index": float(source.institutional_risk_index or 0.0)}
        after_target = {"institutional_risk_index": float(target.institutional_risk_index or 0.0)}

        await log_action(
            db=db,
            risk_id=source.id,
            user_id=current_user.id,
            action="updated",
            previous_values={**before_source},
            new_values={**after_source, "link_added": {"target_risk_id": str(target.id), "link_type": payload.link_type, "weight": payload.weight}},
            request=request,
        )
        await log_action(
            db=db,
            risk_id=target.id,
            user_id=current_user.id,
            action="updated",
            previous_values={**before_target},
            new_values={**after_target, "link_added": {"source_risk_id": str(source.id), "link_type": payload.link_type, "weight": payload.weight}},
            request=request,
        )

        await db.commit()
        await db.refresh(source)

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory:
        background_tasks.add_task(_run_forensic_scan, session_factory)

    links_map = await _build_link_summaries(db, [source.id])
    mit_counts, overdue_counts = await _mitigation_counts(db, [source.id])

    return _risk_to_response(
        source,
        linked=links_map.get(source.id, []),
        mitigation_count=mit_counts.get(source.id, 0),
        overdue_mitigations=overdue_counts.get(source.id, 0),
    )


@router.get("/department/{dept_id}/top5", response_model=List[RiskResponse])
async def department_top5(
    dept_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RiskResponse]:
    if _role(current_user) in DEPT_BOUND_ROLES and current_user.department_id != dept_id:
        raise HTTPException(status_code=403, detail="department-scoped users cannot view other departments")

    stmt = select(Risk).where(Risk.department_id == dept_id).order_by(desc(Risk.risk_score)).limit(5)
    res = await db.execute(stmt)
    risks = res.scalars().all()

    ids = [r.id for r in risks]
    links_map = await _build_link_summaries(db, ids)
    mit_counts, overdue_counts = await _mitigation_counts(db, ids)

    return [
        _risk_to_response(r, links_map.get(r.id, []), mit_counts.get(r.id, 0), overdue_counts.get(r.id, 0))
        for r in risks
    ]


@router.get(
    "/institutional/chains",
    dependencies=[Depends(require_roles("executive", "admin", "risk_officer", "risk_manager"))],
)
async def institutional_chains(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    risks_res = await db.execute(select(Risk))
    risks = risks_res.scalars().all()

    links_res = await db.execute(select(RiskLink))
    links = links_res.scalars().all()

    risks_dict = [{"id": str(r.id)} for r in risks]
    links_dict = [{"source_risk_id": str(l.source_risk_id), "target_risk_id": str(l.target_risk_id)} for l in links]

    clusters = detect_risk_chain(risks_dict, links_dict)

    by_id = {r.id: r for r in risks}

    chains: List[Dict[str, Any]] = []
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        ids = [UUID(rid) for rid in cluster]
        chain_risks = [by_id[i] for i in ids if i in by_id]

        # Use max IRI as a cluster-level summary
        cluster_iri = max([(r.institutional_risk_index or 0.0) for r in chain_risks] or [0.0])

        links_map = await _build_link_summaries(db, ids)
        mit_counts, overdue_counts = await _mitigation_counts(db, ids)

        chains.append(
            {
                "risk_ids": [str(i) for i in ids],
                "iri": cluster_iri,
                "risks": [
                    _risk_to_response(r, links_map.get(r.id, []), mit_counts.get(r.id, 0), overdue_counts.get(r.id, 0)).model_dump()
                    for r in chain_risks
                ],
            }
        )

    return {"chains": chains}


# ---------------------------------------------------------------------------
# Optional forensic export (kept for report downloads)
# ---------------------------------------------------------------------------


@router.get(
    "/{risk_id}/audit/export",
    dependencies=[Depends(require_roles(*ROLE_RISK_SUPERVISOR))],
)
async def export_risk_audit_excel(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    content = await export_audit_log_to_excel(db=db, filters={"risk_id": risk_id})
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=risk_{risk_id}_audit.xlsx"},
    )
