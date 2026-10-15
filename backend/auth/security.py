"""JWT + password hashing utilities.

Manual implementation (no FastAPI-Users) using:
- python-jose for JWT
- passlib[bcrypt] for password hashing
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import HTTPException, status
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_jti_blacklist: set[str] = set()


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)

    to_encode = data.copy()
    to_encode.update(
        {
            "iat": int(now.timestamp()),
            "jti": str(uuid4()),
            "type": token_type,
            "exp": int((now + expires_delta).timestamp()),
        }
    )

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(data, delta, token_type="access")


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(days=settings.refresh_token_expire_days)
    return _create_token(data, delta, token_type="refresh")


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def blacklist_jti(jti: str) -> None:
    _jti_blacklist.add(jti)


def is_jti_blacklisted(jti: str) -> bool:
    return jti in _jti_blacklist
