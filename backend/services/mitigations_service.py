"""Service layer for Mitigations API."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.risk import MitigationAction, MitigationStatus, Risk, RiskStatus
from schemas.mitigation import MitigationCreate, MitigationUpdate
from services.audit_service import log_action
from services.domain_audit_service import log_domain_action
from utils.risk_scorer import calculate_risk_score


def _status_enum(value: str) -> MitigationStatus:
    try:
        return MitigationStatus(value)
    except Exception:
        raise ValueError(f"Invalid mitigation status: {value}")


async def create_mitigation(
    db: AsyncSession,
    risk: Risk,
    payload: MitigationCreate,
    actor_user_id: UUID,
    request=None,
) -> MitigationAction:
    m = MitigationAction(
        risk_id=risk.id,
        description=payload.description,
        assigned_to_id=payload.assigned_to_id,
        due_date=payload.due_date,
        status=MitigationStatus.PENDING,
    )
    db.add(m)
    await db.flush()

    await log_domain_action(
        db,
        entity_type="mitigation",
        entity_id=m.id,
        user_id=actor_user_id,
        action="created",
        previous_values={},
        new_values={
            "risk_id": str(m.risk_id),
            "description": m.description,
            "assigned_to_id": str(m.assigned_to_id),
            "due_date": m.due_date.isoformat(),
            "status": str(m.status.value if hasattr(m.status, "value") else m.status),
        },
        request=request,
    )

    await db.commit()
    await db.refresh(m)
    return m


async def list_mitigations_for_risk(db: AsyncSession, risk_id: UUID) -> List[MitigationAction]:
    stmt = (
        select(MitigationAction)
        .where(MitigationAction.risk_id == risk_id)
        .order_by(MitigationAction.due_date.asc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()


async def get_mitigation(db: AsyncSession, mitigation_id: UUID) -> Optional[MitigationAction]:
    stmt = (
        select(MitigationAction)
        .where(MitigationAction.id == mitigation_id)
        .options(selectinload(MitigationAction.risk))
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def update_mitigation(
    db: AsyncSession,
    mitigation: MitigationAction,
    payload: MitigationUpdate,
    actor_user_id: UUID,
    request=None,
) -> MitigationAction:
    prev = {
        "status": str(mitigation.status.value if hasattr(mitigation.status, "value") else mitigation.status),
        "completion_date": mitigation.completion_date.isoformat() if mitigation.completion_date else None,
        "effectiveness_score": mitigation.effectiveness_score,
        "description": mitigation.description,
        "due_date": mitigation.due_date.isoformat() if mitigation.due_date else None,
        "assigned_to_id": str(mitigation.assigned_to_id),
    }

    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] is not None:
        mitigation.status = _status_enum(data["status"])

    for k in ["completion_date", "effectiveness_score", "description", "due_date", "assigned_to_id"]:
        if k in data:
            setattr(mitigation, k, data[k])

    # Auto-set completion_date when Completed
    if mitigation.status == MitigationStatus.COMPLETED and mitigation.completion_date is None:
        mitigation.completion_date = datetime.now(timezone.utc)

    await log_domain_action(
        db,
        entity_type="mitigation",
        entity_id=mitigation.id,
        user_id=actor_user_id,
        action="updated",
        previous_values=prev,
        new_values={
            "status": str(mitigation.status.value if hasattr(mitigation.status, "value") else mitigation.status),
            "completion_date": mitigation.completion_date.isoformat() if mitigation.completion_date else None,
            "effectiveness_score": mitigation.effectiveness_score,
            "description": mitigation.description,
            "due_date": mitigation.due_date.isoformat() if mitigation.due_date else None,
            "assigned_to_id": str(mitigation.assigned_to_id),
        },
        request=request,
    )

    # When mitigation completed: log to RiskHistory and check if score should be re-evaluated
    risk = mitigation.risk
    if risk and mitigation.status == MitigationStatus.COMPLETED:
        # Score formula doesn"t include mitigations; we still record completion for forensics.
        await log_action(
            db,
            risk_id=risk.id,
            user_id=actor_user_id,
            action="updated",
            previous_values={"mitigation_status": prev.get("status")},
            new_values={
                "mitigation_status": "Completed",
                "mitigation_id": str(mitigation.id),
                "effectiveness_score": mitigation.effectiveness_score,
            },
            request=request,
        )

        # If status is open/in-progress, we can at least bump updated_at and ensure risk_score is consistent.
        try:
            risk.risk_score = float(
                calculate_risk_score(risk.likelihood, risk.impact, risk.velocity, risk.detectability)
            )
        except Exception:
            pass

    await db.commit()
    await db.refresh(mitigation)
    return mitigation


async def list_overdue_mitigations(db: AsyncSession) -> List[MitigationAction]:
    now = datetime.now(timezone.utc)
    stmt = (
        select(MitigationAction)
        .where(and_(MitigationAction.due_date < now, MitigationAction.status != MitigationStatus.COMPLETED))
        .order_by(MitigationAction.due_date.asc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()
