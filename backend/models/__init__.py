"""ORM models package.

At the moment, the canonical SQLAlchemy models live in `models_complete.py`.
This package provides import-stable modules (e.g. `models.risk`) used by the
services layer.
"""

from models_complete import Base  # re-export for Alembic/metadata usage

__all__ = ["Base"]
