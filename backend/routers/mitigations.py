"""Mitigations API router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import DEPT_BOUND_ROLES, get_current_user, get_dept_user, require_roles
from models.risk import Risk, User
from schemas.mitigation import MitigationCreate, MitigationResponse, MitigationUpdate
from services.mitigations_service import (
    create_mitigation,
    get_mitigation,
    list_mitigations_for_risk,
    list_overdue_mitigations,
    update_mitigation,
)
from utils.db_dep import get_db
from sqlalchemy import select

router = APIRouter(prefix="/api/v1", tags=["Mitigations"])


def _role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def _to_response(m) -> MitigationResponse:
    return MitigationResponse(
        id=m.id,
        risk_id=m.risk_id,
        description=m.description,
        assigned_to_id=m.assigned_to_id,
        due_date=m.due_date,
        completion_date=m.completion_date,
        status=str(m.status.value if hasattr(m.status, "value") else m.status),
        effectiveness_score=m.effectiveness_score,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


async def _get_risk(db: AsyncSession, risk_id: UUID) -> Risk:
    res = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = res.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")
    return risk


@router.post("/risks/{risk_id}/mitigations", response_model=MitigationResponse)
async def create_mitigation_endpoint(
    request: Request,
    risk_id: UUID,
    payload: MitigationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("dept_user", "data_clerk", "risk_clerk", "risk_officer", "risk_manager", "department_head", "admin")
    ),
) -> MitigationResponse:
    risk = await _get_risk(db, risk_id)

    if _role(current_user) in DEPT_BOUND_ROLES:
        get_dept_user(current_user, risk)

    m = await create_mitigation(db, risk, payload, actor_user_id=current_user.id, request=request)
    return _to_response(m)


@router.get("/risks/{risk_id}/mitigations", response_model=List[MitigationResponse])
async def list_mitigations_endpoint(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MitigationResponse]:
    risk = await _get_risk(db, risk_id)
    if _role(current_user) in DEPT_BOUND_ROLES:
        get_dept_user(current_user, risk)

    items = await list_mitigations_for_risk(db, risk_id)
    return [_to_response(m) for m in items]


@router.patch("/mitigations/{mitigation_id}", response_model=MitigationResponse)
async def update_mitigation_endpoint(
    request: Request,
    mitigation_id: UUID,
    payload: MitigationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MitigationResponse:
    m = await get_mitigation(db, mitigation_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Mitigation {mitigation_id} not found")

    role = _role(current_user)
    if role not in {"admin", "risk_officer", "risk_manager"} and current_user.id != m.assigned_to_id:
        if not m.risk or role not in DEPT_BOUND_ROLES:
            raise HTTPException(status_code=403, detail="Not permitted")
        get_dept_user(current_user, m.risk)

    try:
        m = await update_mitigation(db, m, payload, actor_user_id=current_user.id, request=request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return _to_response(m)


@router.get("/mitigations/overdue", response_model=List[MitigationResponse])
async def overdue_mitigations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("risk_officer", "risk_manager", "admin")),
) -> List[MitigationResponse]:
    items = await list_overdue_mitigations(db)
    return [_to_response(m) for m in items]
