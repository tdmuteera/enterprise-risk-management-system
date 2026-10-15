# -*- mode: python ; coding: utf-8 -*-
# Run from the `desktop` folder: pyinstaller erm-backend.spec
# Prerequisites: ../FRONT built to ./resources/spa, ../BACK has static/

from pathlib import Path

DESKTOP = Path(SPECPATH).resolve()
BACK = (DESKTOP.parent / "BACK").resolve()
SCRIPT = BACK / "run_desktop.py"
SPA = DESKTOP / "resources" / "spa"
STATIC = BACK / "static"

datas = []
if STATIC.is_dir():
    datas.append((str(STATIC), "static"))
if SPA.is_dir():
    datas.append((str(SPA), "spa"))

hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "bcrypt",
    "passlib.handlers.bcrypt",
    "dns.rdatatype",
    "dns.rdataclass",
    "aiosqlite",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.sql.default_comparator",
    "apscheduler.schedulers.asyncio",
    "apscheduler.triggers.cron",
    "apscheduler.triggers.interval",
    "slowapi",
    "slowapi.middleware",
    "jose",
    "jose.backends",
    "jose.backends.cryptography_backend",
    "models",
    "models.risk",
    "models.alert",
    "routers",
    "routers.auth",
    "routers.risks",
    "routers.departments",
    "routers.users",
    "routers.mitigations",
    "routers.alerts",
    "routers.analytics",
    "routers.reports",
    "routers.audit",
    "services.analytics_service",
    "services.report_service",
    "services.forensic_engine",
    "services.overdue_mitigation_alerts",
    "services.risk_history_archive",
    "services.scoring_service",
    "services.history_archive_service",
    "services.report_cache",
    "services.users_service",
    "services.departments_service",
    "services.mitigations_service",
    "services.alerts_service",
    "services.domain_audit_service",
    "services.audit_service",
    "services.recommendation_engine",
    "auth.dependencies",
    "auth.security",
    "auth.rate_limiter",
    "utils.db_dep",
    "exception_handlers",
    "scheduler",
    "models_complete",
]

block_cipher = None

a = Analysis(
    [str(SCRIPT)],
    pathex=[str(BACK)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="erm-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="erm-backend",
)
