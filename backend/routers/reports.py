"""Reports API router.

Streams generated PDF/Excel files with short-lived caching.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import DEPT_BOUND_ROLES, get_current_user, require_roles
from models.risk import User
from services.report_cache import cache_key, get_or_create_async
from services.report_service import (
    generate_department_report,
    generate_executive_report,
    generate_forensic_audit_report,
    generate_institutional_report,
)
from utils.db_dep import get_db

router = APIRouter(tags=["Reports"])


def _role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def _stream_file(path: Path, filename: str, content_type: str) -> StreamingResponse:
    def _iterfile():
        with open(path, "rb") as f:
            while True:
                chunk = f.read(1024 * 256)
                if not chunk:
                    break
                yield chunk

    headers = {"Content-Disposition": f"attachment; filename=\"{filename}\""}
    return StreamingResponse(_iterfile(), media_type=content_type, headers=headers)


def _parse_report_datetime(value: Optional[str], field_name: str) -> Optional[datetime]:
    if value is None or value == "":
        return None
    raw = value.strip()
    # Accept ISO date, ISO datetime, and common dd/mm/yyyy format from UI locales.
    try:
        if "T" in raw or " " in raw:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if "-" in raw:
            return datetime.fromisoformat(f"{raw}T00:00:00")
        if "/" in raw:
            day, month, year = raw.split("/")
            return datetime(int(year), int(month), int(day))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid {field_name} format: {value}") from exc
    raise HTTPException(status_code=422, detail=f"Invalid {field_name} format: {value}")


@router.get("/department/{dept_id}")
async def department_report(
    request: Request,
    dept_id: UUID,
    format: str = Query("pdf"),
    file_type: Optional[str] = Query(None),
    export_format: Optional[str] = Query(None),
    fileType: Optional[str] = Query(None, alias="fileType"),
    exportFormat: Optional[str] = Query(None, alias="exportFormat"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    startDate: Optional[str] = Query(None, alias="startDate"),
    endDate: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_start = startDate if startDate is not None else start_date
    raw_end = endDate if endDate is not None else end_date
    start_dt = _parse_report_datetime(raw_start, "start_date")
    end_dt = _parse_report_datetime(raw_end, "end_date")
    # Department-bound roles can only access their own department report
    if _role(current_user) in DEPT_BOUND_ROLES:
        if not current_user.department_id or current_user.department_id != dept_id:
            raise HTTPException(status_code=403, detail="Cannot access reports outside your department")

    raw_fmt = exportFormat or fileType or export_format or file_type or format or "pdf"
    fmt = raw_fmt.lower().strip()
    aliases = {
        "xlsx": "excel",
        "xls": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
        "application/vnd.ms-excel": "xls",
        "application/pdf": "pdf",
        "text/csv": "csv",
    }
    fmt = aliases.get(fmt, fmt)
    if fmt not in {"pdf", "excel", "xls", "csv"}:
        raise HTTPException(status_code=422, detail="format must be one of: pdf, excel, xls, csv")
    ext = "pdf" if fmt == "pdf" else "csv" if fmt == "csv" else "xls" if fmt == "xls" else "xlsx"

    key = cache_key(
        "department",
        str(dept_id),
        fmt,
        str(start_dt or ""),
        str(end_dt or ""),
        str(current_user.id),
    )

    meta_holder: dict = {}

    async def _gen(tmp_path: Path) -> None:
        meta_holder["meta"] = await generate_department_report(
            db=db,
            dept_id=dept_id,
            fmt=fmt,
            start_date=start_dt,
            end_date=end_dt,
            generated_by=current_user.full_name,
            out_path=tmp_path,
        )

    try:
        hit = await get_or_create_async(key, ext, ttl_seconds=600, generator=_gen)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    meta = meta_holder.get("meta")
    if not meta:
        # If cache hit, we still need meta for headers; regenerate lightweight meta.
        # Use conservative defaults based on format.
        meta = type("M", (), {})()
        meta.filename = f"department-report.{ext}"
        if ext == "pdf":
            meta.content_type = "application/pdf"
        elif ext == "xls":
            meta.content_type = "application/vnd.ms-excel"
        else:
            meta.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return _stream_file(hit.path, meta.filename, meta.content_type)


@router.get("/institutional")
async def institutional_report(
    request: Request,
    format: str = Query("pdf", pattern="^(pdf)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("executive", "admin", "risk_officer", "risk_manager")),
):
    key = cache_key("institutional", "pdf", str(current_user.id))

    meta_holder: dict = {}

    async def _gen(tmp_path: Path) -> None:
        meta_holder["meta"] = await generate_institutional_report(db, tmp_path, generated_by=current_user.full_name)

    hit = await get_or_create_async(key, "pdf", ttl_seconds=600, generator=_gen)
    meta = meta_holder.get("meta") or type("M", (), {"filename": "institutional-risk-report.pdf", "content_type": "application/pdf"})()
    return _stream_file(hit.path, meta.filename, meta.content_type)


@router.get("/executive")
async def executive_report(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("executive", "admin", "risk_officer", "risk_manager")),
):
    key = cache_key("executive", "pdf", str(current_user.id))

    meta_holder: dict = {}

    async def _gen(tmp_path: Path) -> None:
        meta_holder["meta"] = await generate_executive_report(db, tmp_path, generated_by=current_user.full_name)

    hit = await get_or_create_async(key, "pdf", ttl_seconds=600, generator=_gen)
    meta = meta_holder.get("meta") or type("M", (), {"filename": "executive-summary.pdf", "content_type": "application/pdf"})()
    return _stream_file(hit.path, meta.filename, meta.content_type)


@router.get("/forensic-audit")
async def forensic_audit_report(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "risk_officer", "risk_manager", "department_head")),
):
    start_dt = _parse_report_datetime(start_date, "start_date")
    end_dt = _parse_report_datetime(end_date, "end_date")
    key = cache_key("forensic-audit-v2", str(start_dt or ""), str(end_dt or ""), str(current_user.id))

    meta_holder: dict = {}

    async def _gen(tmp_path: Path) -> None:
        meta_holder["meta"] = await generate_forensic_audit_report(
            db,
            tmp_path,
            generated_by=current_user.full_name,
            start_date=start_dt,
            end_date=end_dt,
        )

    hit = await get_or_create_async(key, "xlsx", ttl_seconds=120, generator=_gen)
    meta = meta_holder.get("meta") or type(
        "M",
        (),
        {
            "filename": "forensic-audit.xlsx",
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
    )()
    return _stream_file(hit.path, meta.filename, meta.content_type)
