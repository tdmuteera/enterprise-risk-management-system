"""models.alert

Enum re-exports for alerts.

`models_complete.py` defines the Alert enums used across the system.
Some services refer to an older name `AlertCreatedForRole`; we keep it as an
alias to `AlertRole`.
"""

from models_complete import AlertRole, AlertSeverity, AlertType

# Backwards-compatible alias
AlertCreatedForRole = AlertRole

__all__ = [
    "AlertType",
    "AlertSeverity",
    "AlertRole",
    "AlertCreatedForRole",
]
