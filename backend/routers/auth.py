"""Auth routes: login/refresh/logout/me.

Manual JWT implementation using python-jose and passlib[bcrypt].
"""

from typing import Any, Dict, Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.dependencies import get_current_user
from auth.rate_limiter import limiter
from utils.db_dep import get_db
from auth.security import (
    blacklist_jti,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token,
)
from config import settings
from models.risk import Department, SecurityEvent, User, UserRole

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: Literal["risk_officer", "dept_user", "data_clerk", "risk_clerk"] = "dept_user"
    department_id: Optional[UUID] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class MeUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8)


async def _log_security_event(
    db: AsyncSession,
    email_attempted: str,
    ip: Optional[str],
    reason: str,
) -> None:
    ev = SecurityEvent(email_attempted=email_attempted, ip_address=ip, reason=reason)
    db.add(ev)
    await db.commit()


def _client_ip(request: Request) -> Optional[str]:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip() or None
    return request.client.host if request.client else None


@router.post("/login")
@limiter.limit("60/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    ip = _client_ip(request)

    email_norm = str(payload.email).strip().lower()

    result = await db.execute(
        select(User)
        .where(User.email == email_norm)
        .options(selectinload(User.department))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        await _log_security_event(db, email_norm, ip, "invalid_credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        await _log_security_event(db, email_norm, ip, "inactive_user")
        raise HTTPException(status_code=401, detail="User inactive")

    token_data = {
        "sub": str(user.id),
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "department_id": str(user.department_id) if user.department_id else None,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.full_name,
            "role": token_data["role"],
            "dept": user.department.name if user.department else None,
            "department_id": token_data["department_id"],
        },
    }


@router.post("/register")
@limiter.limit("60/hour")
async def register(
    request: Request,
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Create a department-scoped user account (open registration when enabled in settings)."""
    if not settings.allow_open_registration:
        raise HTTPException(
            status_code=403,
            detail="Open registration is disabled. Contact an administrator for an account.",
        )

    email_norm = str(payload.email).lower().strip()

    existing = await db.execute(select(User).where(User.email == email_norm))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    role_map = {
        "risk_officer": UserRole.RISK_OFFICER,
        "dept_user": UserRole.DEPT_USER,
        "data_clerk": UserRole.DATA_CLERK,
        "risk_clerk": UserRole.RISK_CLERK,
    }
    selected_role = role_map[payload.role]

    dept = None
    if selected_role in {UserRole.DEPT_USER, UserRole.DATA_CLERK, UserRole.RISK_CLERK}:
        if not payload.department_id:
            raise HTTPException(status_code=422, detail="department_id is required for department-scoped users")
        dres = await db.execute(
            select(Department).where(Department.id == payload.department_id, Department.is_active.is_(True))
        )
        dept = dres.scalar_one_or_none()
        if not dept:
            raise HTTPException(status_code=422, detail="Invalid or inactive department")

    user = User(
        email=email_norm,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=selected_role,
        department_id=payload.department_id,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token_data = {
        "sub": str(user.id),
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "department_id": str(user.department_id) if user.department_id else None,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.full_name,
            "role": token_data["role"],
            "dept": dept.name if dept else None,
            "department_id": token_data["department_id"],
        },
    }


@router.post("/refresh")
async def refresh(payload: RefreshRequest) -> Dict[str, Any]:
    token_payload = decode_token(payload.refresh_token)
    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token required")

    token_data = {
        "sub": token_payload.get("sub"),
        "role": token_payload.get("role"),
        "department_id": token_payload.get("department_id"),
    }

    return {"access_token": create_access_token(token_data), "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    payload = getattr(request.state, "token_payload", None)
    if not payload:
        raise HTTPException(status_code=401, detail="Not authenticated")

    jti = payload.get("jti")
    if jti:
        blacklist_jti(str(jti))

    return {"status": "ok"}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.full_name,
        "role": current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
        "department_id": str(current_user.department_id) if current_user.department_id else None,
    }


@router.put("/me")
async def update_me(
    payload: MeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.password is not None:
        current_user.hashed_password = hash_password(payload.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.full_name,
        "role": current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
        "department_id": str(current_user.department_id) if current_user.department_id else None,
    }
