"""
Build a pre-seeded SQLite file for the desktop installer.

Run from the BACK folder (with venv active):
  python build_desktop_seed.py

Writes: ../desktop/resources/erm_seed.db
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    back = Path(__file__).resolve().parent
    repo = back.parent
    out = repo / "desktop" / "resources" / "erm_seed.db"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    db_url = f"sqlite+aiosqlite:///{out.as_posix()}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["DB_URL"] = db_url
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "false"

    # Ensure clean import of settings with env above
    sys.path.insert(0, str(back))
    os.chdir(back)
    os.environ["DATABASE_URL"] = db_url
    os.environ["DB_URL"] = db_url

    async def _run() -> None:
        from sqlalchemy.ext.asyncio import create_async_engine

        from models_complete import Base

        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

        # Import after tables exist
        import importlib.util

        spec = importlib.util.spec_from_file_location("db_seed", back / "db_seed.py")
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        await mod.seed_database()

    asyncio.run(_run())
    print(f"Wrote seeded database: {out}")


if __name__ == "__main__":
    main()
