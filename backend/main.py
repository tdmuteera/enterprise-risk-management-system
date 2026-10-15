"""
FastAPI main application entry point for ERM Platform.
Initializes database connection, CORS, and lifespan events.
"""

import logging
import os
import sys
import json
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from config import settings
from database import init_db_engine, get_session, check_db_connection
from exception_handlers import (
    integrity_error_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)
from scheduler import register_scheduler

from routers.risks import router as risks_router
from routers.auth import router as auth_router
from routers.departments import router as departments_router
from routers.users import router as users_router
from routers.mitigations import router as mitigations_router
from routers.alerts import router as alerts_router
from routers.analytics import router as analytics_router
from routers.reports import router as reports_router
from routers.audit import router as audit_router

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from auth.rate_limiter import limiter
from starlette.responses import FileResponse

# Configure logging
_log_level = getattr(logging, str(settings.log_level).upper(), logging.INFO)
logging.basicConfig(
    level=_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _app_base_dir() -> str:
    """Project root when running from source; PyInstaller bundle root when frozen."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return meipass
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# Global database engine and session factory
db_engine: AsyncEngine = None
session_factory = None


def _ensure_directories():
    """Ensure all required directories exist."""
    if getattr(sys, "frozen", False):
        # PyInstaller bundle already contains packages; avoid mkdir under install dir (read-only).
        return
    base_path = Path(_app_base_dir())
    directories = ["models", "schemas", "routers", "services", "utils", "tests", "static", "alembic", "auth"]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(exist_ok=True)
        
        # Create __init__.py for Python packages
        if directory not in ["static"]:
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Auto-generated package module."""\n')
    
    # Create .vscode settings
    vscode_dir = base_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    vscode_settings = vscode_dir / "settings.json"
    if not vscode_settings.exists():
        settings = {"python.terminal.useEnvFile": True}
        vscode_settings.write_text(json.dumps(settings, indent=2))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup
    global db_engine, session_factory
    
    _ensure_directories()
    logger.info("=" * 80)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📅 Server start time: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    try:
        # Initialize database engine
        db_engine = await init_db_engine()
        session_factory = await get_session(db_engine)
        
        # Verify database connectivity
        is_connected = await check_db_connection(db_engine)
        if not is_connected:
            logger.warning("⚠️  Database connection check failed - proceeding with caution")

        # Make session factory available to routers via app.state
        app.state.session_factory = session_factory

        scheduler = register_scheduler(session_factory)
        scheduler.start()
        app.state.scheduler = scheduler
        logger.info(
            "✓ APScheduler started (forensic 6h, scores 23:00 UTC, overdue hourly, archive 30d)"
        )
        
        logger.info(f"✓ CORS origins: {settings.allowed_origins}")
        logger.info(f"✓ Debug mode: {settings.effective_debug}")
        
    except Exception as e:
        logger.error(f"✗ Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down server...")

    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("✓ APScheduler stopped")

    if db_engine:
        await db_engine.dispose()
        logger.info("✓ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent Enterprise Risk Management Platform for Zimbabwean Universities",
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Rate limiting (SlowAPI)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Mount static files for reports
static_path = os.path.join(_app_base_dir(), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns server status, database connectivity, and version.
    """
    db_status = "connected" if db_engine else "disconnected"
    
    if db_engine:
        try:
            from sqlalchemy import text
            async with db_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
    
    return {
        "status": "ok",
        "db": db_status,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat(),
    }


# Root endpoint (API mode only; desktop serves SPA at /)
if os.environ.get("ERM_DESKTOP") != "1":

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint - API information."""
        return {
            "message": "Welcome to the ERM Platform API",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }


# Routers
app.include_router(auth_router)
app.include_router(risks_router)
app.include_router(departments_router)
app.include_router(users_router)
app.include_router(mitigations_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(reports_router, prefix="/api/v1/reports")
app.include_router(reports_router, prefix="/reports")
app.include_router(audit_router)


# API Router placeholder
@app.get("/api/v1/info", tags=["Info"])
async def api_info():
    """API information endpoint."""
    return {
        "api_version": "v1",
        "status": "operational",
        "environment": settings.environment,
    }


def _register_desktop_spa(application: FastAPI) -> None:
    """Serve built React app from the same origin (Electron / local desktop)."""
    if os.environ.get("ERM_DESKTOP") != "1":
        return
    spa_dir = os.environ.get("ERM_SPA_DIR", "").strip()
    if not spa_dir or not os.path.isdir(spa_dir):
        logger.warning("ERM_DESKTOP is set but ERM_SPA_DIR is missing or not a directory")
        return
    index_path = os.path.join(spa_dir, "index.html")
    if not os.path.isfile(index_path):
        logger.warning("SPA index.html not found in %s", spa_dir)
        return

    @application.get("/", include_in_schema=False)
    async def desktop_root():
        return FileResponse(index_path)

    @application.get("/{full_path:path}", include_in_schema=False)
    async def desktop_spa(full_path: str):
        lower = full_path.lower()
        # Unregistered /api/... paths fall through here (registered API uses "" not "/" so
        # /api/v1/... matches axios without a trailing slash). Return explicit 404, not index.html.
        if lower.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = os.path.join(spa_dir, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(index_path)


_register_desktop_spa(app)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.effective_debug,
        log_level="info",
    )
