"""Departments API router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_roles
from models.risk import User
from schemas.department import (
    DepartmentCreate,
    DepartmentDetailResponse,
    DepartmentResponse,
    DepartmentSummaryResponse,
    DepartmentUpdate,
)
from schemas.risk import RiskListResponse
from services.departments_service import (
    create_department,
    get_department,
    get_department_iri,
    get_department_open_risk_count,
    get_department_risks,
    get_department_summary,
    list_active_departments,
    update_department,
)
from utils.db_dep import get_db

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
async def list_departments(db: AsyncSession = Depends(get_db)) -> List[DepartmentResponse]:
    depts = await list_active_departments(db)
    return [
        DepartmentResponse(
            id=d.id,
            name=d.name,
            code=d.code,
            description=d.description,
            head_of_dept=d.head_of_dept,
            is_active=bool(d.is_active),
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in depts
    ]


@router.post("", response_model=DepartmentResponse)
async def create_department_endpoint(
    request: Request,
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> DepartmentResponse:
    dept = await create_department(db, payload, user_id=current_user.id, request=request)
    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        description=dept.description,
        head_of_dept=dept.head_of_dept,
        is_active=bool(dept.is_active),
        created_at=dept.created_at,
        updated_at=dept.updated_at,
    )


@router.get("/{dept_id}", response_model=DepartmentDetailResponse)
async def get_department_endpoint(dept_id: UUID, db: AsyncSession = Depends(get_db)) -> DepartmentDetailResponse:
    dept = await get_department(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department {dept_id} not found")

    open_count = await get_department_open_risk_count(db, dept_id)
    iri = await get_department_iri(db, dept_id)

    return DepartmentDetailResponse(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        description=dept.description,
        head_of_dept=dept.head_of_dept,
        is_active=bool(dept.is_active),
        created_at=dept.created_at,
        updated_at=dept.updated_at,
        open_risks_count=open_count,
        iri=iri,
    )


@router.put("/{dept_id}", response_model=DepartmentResponse)
async def update_department_endpoint(
    request: Request,
    dept_id: UUID,
    payload: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> DepartmentResponse:
    dept = await get_department(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department {dept_id} not found")

    dept = await update_department(db, dept, payload, user_id=current_user.id, request=request)
    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        description=dept.description,
        head_of_dept=dept.head_of_dept,
        is_active=bool(dept.is_active),
        created_at=dept.created_at,
        updated_at=dept.updated_at,
    )


@router.get("/{dept_id}/risks", response_model=RiskListResponse)
async def list_department_risks(
    request: Request,
    dept_id: UUID,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskListResponse:
    items, total, top5 = await get_department_risks(db, dept_id, page=page, page_size=page_size)
    return RiskListResponse(items=items, total=total, page=page, page_size=page_size, top_5=top5)


@router.get("/{dept_id}/summary", response_model=DepartmentSummaryResponse)
async def department_summary(
    dept_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentSummaryResponse:
    dept = await get_department(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department {dept_id} not found")

    total, counts, top5, iri, trend = await get_department_summary(db, dept_id)

    return DepartmentSummaryResponse(
        total_risks=total,
        critical=counts.get("Critical", 0),
        high=counts.get("High", 0),
        medium=counts.get("Medium", 0),
        low=counts.get("Low", 0),
        top5_risks=top5,
        iri=iri,
        trend=trend,
    )
