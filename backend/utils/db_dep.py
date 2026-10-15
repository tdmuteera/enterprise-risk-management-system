"""Shared DB session dependency.

Uses the app's `app.state.session_factory` set during lifespan startup.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Database session factory not initialized")

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
