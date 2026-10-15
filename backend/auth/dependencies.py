"""FastAPI dependencies for JWT auth, RBAC, and department scoping."""

from __future__ import annotations

from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import decode_token, is_jti_blacklisted
from models.risk import Risk, User
from utils.db_dep import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Roles that must stay within their department for risk access (read/write via get_dept_user).
DEPT_BOUND_ROLES = frozenset({"dept_user", "data_clerk", "risk_clerk", "department_head"})


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    if jti and is_jti_blacklisted(str(jti)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(str(sub))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # allow downstream handlers (e.g., /logout) to access token claims
    request.state.token_payload = payload
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    def _checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        if role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _checker


def get_dept_user(current_user: User, risk: Risk) -> User:
    """Enforce department scoping for department-bound roles."""

    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

    if role in DEPT_BOUND_ROLES:
        if not current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This role must belong to a department to access department-scoped risks",
            )
        if risk.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access risks outside your department",
            )

    return current_user
