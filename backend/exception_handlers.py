"""Global exception handlers for consistent API errors."""

from __future__ import annotations

import logging
import sys
import traceback
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _friendly_integrity_message(exc: IntegrityError) -> str:
    raw = str(exc.orig) if getattr(exc, "orig", None) else str(exc)
    lower = raw.lower()
    if "unique" in lower or "duplicate" in lower:
        return "A record with this value already exists."
    if "foreign key" in lower:
        return "Related record is missing or cannot be linked."
    if "not null" in lower:
        return "Required field is missing."
    return "This operation conflicts with existing data."


def validation_error_payload(errors: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for err in errors:
        loc = err.get("loc") or ()
        parts: list[str] = []
        for p in loc:
            if str(p) in ("body", "query", "path", "header", "cookie"):
                continue
            parts.append(str(p))
        field = ".".join(parts) if parts else "request"
        msg = str(err.get("msg", "Invalid input"))
        out.append({"field": field, "message": msg})
    return out


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    payload = validation_error_payload(exc.errors())
    return JSONResponse(status_code=422, content={"detail": payload})


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": _friendly_integrity_message(exc)},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, StarletteHTTPException):
        detail = exc.detail
        if not isinstance(detail, (str, dict, list)):
            detail = str(detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": detail})

    logger.error("Unhandled server error: %s", exc, exc_info=True)
    print(traceback.format_exc(), file=sys.stderr, flush=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Our team has been notified."},
    )
