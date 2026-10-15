"""
Desktop entrypoint for the ERM API (used by Electron + PyInstaller).

Sets environment before any app imports, then runs uvicorn on 127.0.0.1.

Usage (dev, from BACK folder):
  python run_desktop.py --port 17890 --data-dir "C:\\path\\userData"

Packaged:
  erm-backend.exe --port 17890 --data-dir <Electron userData>
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import shutil
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _sqlite_url(db_file: Path) -> str:
    # Three slashes after scheme for absolute path on Windows/Linux
    return f"sqlite+aiosqlite:///{db_file.as_posix()}"


async def _ensure_schema(db_url: str) -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    from models_complete import Base

    engine = create_async_engine(db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


def _copy_seed_if_needed(db_file: Path, seed_path: str | None) -> None:
    if db_file.exists():
        return
    db_file.parent.mkdir(parents=True, exist_ok=True)
    if seed_path and Path(seed_path).is_file():
        shutil.copy2(seed_path, db_file)
        logger.info("Copied bundled seed database to %s", db_file)
        return
    logger.warning("No seed DB at %s — creating empty schema", seed_path)
    asyncio.run(_ensure_schema(_sqlite_url(db_file)))


def _spa_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            p = Path(meipass) / "spa"
            if p.is_dir():
                return p
        exe_dir = Path(sys.executable).resolve().parent
        if (exe_dir / "spa").is_dir():
            return exe_dir / "spa"
        internal = exe_dir / "_internal" / "spa"
        if internal.is_dir():
            return internal
        return exe_dir / "spa"
    return Path(__file__).resolve().parent.parent / "FRONT" / "dist"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="ERM desktop API server")
    parser.add_argument("--port", type=int, default=17890)
    parser.add_argument("--data-dir", type=str, required=True, help="Writable folder for erm.db")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    db_file = data_dir / "erm.db"
    seed = os.environ.get("ERM_SEED_DB", "").strip() or None

    _copy_seed_if_needed(db_file, seed)

    spa = _spa_dir()
    if not spa.is_dir() or not (spa / "index.html").is_file():
        logger.error("SPA not found at %s — build the frontend (npm run build) first.", spa)
        sys.exit(1)

    db_url = _sqlite_url(db_file)
    port = args.port
    origin = f"http://127.0.0.1:{port}"

    # Must be set before uvicorn imports main -> config
    os.environ["ERM_DESKTOP"] = "1"
    os.environ["DATABASE_URL"] = db_url
    os.environ["DB_URL"] = db_url
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "false"
    os.environ["ERM_SPA_DIR"] = str(spa)
    os.environ["CORS_ORIGINS"] = f"{origin},http://localhost:{port}"
    os.environ.setdefault(
        "SECRET_KEY",
        "desktop-prototype-only-change-for-custom-builds-erm-v1",
    )
    os.environ.setdefault("ALLOW_OPEN_REGISTRATION", "true")

    import uvicorn

    # Import app so PyInstaller traces all dependencies (string form would miss them)
    import main as main_module

    logger.info("Starting ERM desktop API on %s (db=%s)", origin, db_file)
    uvicorn.run(
        main_module.app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        reload=False,
        factory=False,
    )


if __name__ == "__main__":
    main()
