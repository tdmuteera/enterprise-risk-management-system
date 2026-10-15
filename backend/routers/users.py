"""Users API router."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_roles
from models.risk import User
from schemas.user import UserCreate, UserResponse, UserUpdateAdmin, UserUpdateSelf
from services.users_service import (
    create_user,
    deactivate_user,
    get_user,
    list_users,
    update_user_admin,
    update_user_self,
)
from utils.db_dep import get_db

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


@router.get("", response_model=List[UserResponse])
async def list_users_endpoint(
    role: Optional[str] = None,
    dept: Optional[UUID] = None,
    active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> List[UserResponse]:
    try:
        users = await list_users(db, role=role, dept_id=dept, active=active)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=_role(u),
            department_id=u.department_id,
            is_active=bool(u.is_active),
            last_login=u.last_login,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]


@router.post("", response_model=UserResponse)
async def create_user_endpoint(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> UserResponse:
    try:
        user = await create_user(db, payload, actor_user_id=current_user.id, request=request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=_role(user),
        department_id=user.department_id,
        is_active=bool(user.is_active),
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    role = _role(current_user)
    if role not in {"admin", "risk_officer"} and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not permitted")

    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=_role(user),
        department_id=user.department_id,
        is_active=bool(user.is_active),
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    request: Request,
    user_id: UUID,
    payload: UserUpdateAdmin | UserUpdateSelf,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    role = _role(current_user)

    if role == "admin":
        try:
            updated = await update_user_admin(
                db,
                user,
                UserUpdateAdmin(**payload.model_dump(exclude_unset=True)),
                actor_user_id=current_user.id,
                request=request,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    elif current_user.id == user_id:
        # self-update only
        updated = await update_user_self(db, user, UserUpdateSelf(**payload.model_dump(exclude_unset=True)), actor_user_id=current_user.id, request=request)
    else:
        raise HTTPException(status_code=403, detail="Not permitted")

    return UserResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        role=_role(updated),
        department_id=updated.department_id,
        is_active=bool(updated.is_active),
        last_login=updated.last_login,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user_endpoint(
    request: Request,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> UserResponse:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    updated = await deactivate_user(db, user, actor_user_id=current_user.id, request=request)
    return UserResponse(
        id=updated.id,
        email=updated.email,
        full_name=updated.full_name,
        role=_role(updated),
        department_id=updated.department_id,
        is_active=bool(updated.is_active),
        last_login=updated.last_login,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )
