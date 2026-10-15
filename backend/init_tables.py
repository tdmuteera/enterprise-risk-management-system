"""One-shot: create all ORM tables (dev / first run). Usage: python init_tables.py"""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from config import settings
from models_complete import Base


async def main() -> None:
    engine = create_async_engine(settings.db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tables created (create_all).")


if __name__ == "__main__":
    asyncio.run(main())
