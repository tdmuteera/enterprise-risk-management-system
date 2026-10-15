"""models.risk

Compatibility layer.

This project keeps the canonical ORM definitions in `models_complete.py`, but
services import from `models.risk`. This module re-exports the ORM models and
related enums so those imports work without forcing a full file split yet.
"""

from models_complete import (  # noqa: F401
    Alert,
    AlertRole,
    AlertSeverity,
    AlertType,
    Department,
    DomainAuditEvent,
    MitigationAction,
    MitigationStatus,
    Risk,
    RiskCategory,
    RiskHistory,
    RiskHistoryArchive,
    RiskHistoryAction,
    RiskLink,
    RiskLinkType,
    RiskStatus,
    RiskType,
    SecurityEvent,
    User,
    UserRole,
)

__all__ = [
    "Risk",
    "RiskHistory",
    "RiskHistoryArchive",
    "RiskLink",
    "MitigationAction",
    "Alert",
    "Department",
    "SecurityEvent",
    "DomainAuditEvent",
    "User",
    "UserRole",
    "RiskCategory",
    "RiskStatus",
    "RiskType",
    "RiskLinkType",
    "RiskHistoryAction",
    "MitigationStatus",
    "AlertType",
    "AlertSeverity",
    "AlertRole",
]
