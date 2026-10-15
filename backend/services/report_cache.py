"""Simple on-disk report cache.

Caches generated report files for a short TTL so repeated downloads with the
same parameters are fast.

Windows note: uses the OS temp directory (tempfile.gettempdir()).
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable

AsyncGen = Callable[[Path], Awaitable[None]]


@dataclass(frozen=True)
class CacheHit:
    path: Path
    is_hit: bool


def _cache_dir() -> Path:
    base = Path(tempfile.gettempdir()) / "erm-reports-cache"
    base.mkdir(parents=True, exist_ok=True)
    return base


def cache_key(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update((p or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def get_or_create(
    key: str,
    extension: str,
    ttl_seconds: int,
    generator: Callable[[Path], None],
) -> CacheHit:
    """Return cached file path if present+fresh else generate it."""

    extension = extension.lstrip(".")
    path = _cache_dir() / f"{key}.{extension}"

    if path.exists():
        age = time.time() - path.stat().st_mtime
        if age <= ttl_seconds:
            return CacheHit(path=path, is_hit=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        generator(tmp_path)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return CacheHit(path=path, is_hit=False)


async def get_or_create_async(
    key: str,
    extension: str,
    ttl_seconds: int,
    generator: AsyncGen,
) -> CacheHit:
    """Async variant for use inside FastAPI (never call sync ``anyio.run`` from a running loop)."""

    extension = extension.lstrip(".")
    path = _cache_dir() / f"{key}.{extension}"

    if path.exists():
        age = time.time() - path.stat().st_mtime
        if age <= ttl_seconds:
            return CacheHit(path=path, is_hit=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        await generator(tmp_path)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return CacheHit(path=path, is_hit=False)
