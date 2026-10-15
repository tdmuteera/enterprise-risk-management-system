"""Service layer for Users API."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from models.risk import Department, User, UserRole
from schemas.user import UserCreate, UserUpdateAdmin, UserUpdateSelf
from services.domain_audit_service import log_domain_action

logger = logging.getLogger(__name__)


def _role_str(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _send_welcome_email_stub(email: str) -> None:
    # Stubbed on purpose: integrate real email provider later.
    logger.info("[welcome-email] Would send welcome email to %s", email)


async def list_users(
    db: AsyncSession,
    role: Optional[str] = None,
    dept_id: Optional[UUID] = None,
    active: Optional[bool] = None,
) -> List[User]:
    conditions = []
    if role:
        try:
            role_enum = UserRole(role)
        except Exception:
            raise ValueError(f"Invalid role: {role}")
        conditions.append(User.role == role_enum)
    if dept_id:
        conditions.append(User.department_id == dept_id)
    if active is not None:
        conditions.append(User.is_active == active)

    stmt = select(User).where(and_(*conditions)) if conditions else select(User)
    stmt = stmt.order_by(User.full_name.asc())
    res = await db.execute(stmt)
    return res.scalars().all()


async def create_user(
    db: AsyncSession,
    payload: UserCreate,
    actor_user_id: UUID,
    request=None,
) -> User:
    # Ensure department exists if provided
    if payload.department_id:
        dep_res = await db.execute(select(Department).where(Department.id == payload.department_id))
        if not dep_res.scalar_one_or_none():
            raise ValueError(f"Department {payload.department_id} not found")

    try:
        role_enum = UserRole(payload.role)
    except Exception:
        raise ValueError(f"Invalid role: {payload.role}")

    user = User(
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=role_enum,
        department_id=payload.department_id,
        is_active=payload.is_active,
    )
    db.add(user)

    try:
        await db.flush()
    except IntegrityError:
        raise ValueError("User with that email already exists")

    await log_domain_action(
        db,
        entity_type="user",
        entity_id=user.id,
        user_id=actor_user_id,
        action="created",
        previous_values={},
        new_values={
            "email": user.email,
            "full_name": user.full_name,
            "role": _role_str(user.role),
            "department_id": str(user.department_id) if user.department_id else None,
            "is_active": user.is_active,
        },
        request=request,
    )

    await db.commit()
    await db.refresh(user)

    _send_welcome_email_stub(user.email)
    return user


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def update_user_admin(
    db: AsyncSession,
    user: User,
    payload: UserUpdateAdmin,
    actor_user_id: UUID,
    request=None,
) -> User:
    prev = {
        "full_name": user.full_name,
        "role": _role_str(user.role),
        "department_id": str(user.department_id) if user.department_id else None,
        "is_active": user.is_active,
    }

    data = payload.model_dump(exclude_unset=True)

    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data.pop("password"))

    if "role" in data and data["role"] is not None:
        try:
            user.role = UserRole(data["role"])
        except Exception:
            raise ValueError(f"Invalid role: {data['role']}")

    if "department_id" in data:
        user.department_id = data["department_id"]

    for k in ["full_name", "is_active"]:
        if k in data:
            setattr(user, k, data[k])

    await log_domain_action(
        db,
        entity_type="user",
        entity_id=user.id,
        user_id=actor_user_id,
        action="updated",
        previous_values=prev,
        new_values={
            "full_name": user.full_name,
            "role": _role_str(user.role),
            "department_id": str(user.department_id) if user.department_id else None,
            "is_active": user.is_active,
        },
        request=request,
    )

    await db.commit()
    await db.refresh(user)
    return user


async def update_user_self(
    db: AsyncSession,
    user: User,
    payload: UserUpdateSelf,
    actor_user_id: UUID,
    request=None,
) -> User:
    prev = {"full_name": user.full_name}

    data = payload.model_dump(exclude_unset=True)

    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data["password"])

    if "full_name" in data and data["full_name"]:
        user.full_name = data["full_name"]

    await log_domain_action(
        db,
        entity_type="user",
        entity_id=user.id,
        user_id=actor_user_id,
        action="updated",
        previous_values=prev,
        new_values={"full_name": user.full_name},
        request=request,
    )

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(
    db: AsyncSession,
    user: User,
    actor_user_id: UUID,
    request=None,
) -> User:
    prev = {"is_active": user.is_active}
    user.is_active = False

    await log_domain_action(
        db,
        entity_type="user",
        entity_id=user.id,
        user_id=actor_user_id,
        action="deleted",
        previous_values=prev,
        new_values={"is_active": user.is_active},
        request=request,
    )

    await db.commit()
    await db.refresh(user)
    return user
