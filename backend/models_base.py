"""
Shared base model and enumerations for ERM Platform.
All models inherit from this Base and include created_at/updated_at.
"""

from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from enum import Enum

# Declarative base for all models
Base = declarative_base()


# ============================================================================
# ENUMERATIONS
# ============================================================================

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    RISK_OFFICER = "risk_officer"
    DEPT_USER = "dept_user"
    EXECUTIVE = "executive"


class RiskCategory(str, Enum):
    """Risk category enumeration."""
    FINANCIAL = "Financial"
    HR = "HR"
    ACADEMIC = "Academic"
    IT = "IT"
    COMPLIANCE = "Compliance"
    OPERATIONAL = "Operational"
    REPUTATIONAL = "Reputational"


class RiskStatus(str, Enum):
    """Risk status enumeration."""
    OPEN = "Open"
    IN_PROGRESS = "In-Progress"
    MITIGATED = "Mitigated"
    CLOSED = "Closed"
    ESCALATED = "Escalated"


class RiskLinkType(str, Enum):
    """Risk link type enumeration."""
    CAUSES = "causes"
    RELATED_TO = "related_to"
    ESCALATES = "escalates"
    TRIGGERS = "triggers"


class RiskHistoryAction(str, Enum):
    """Risk history action enumeration."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    SCORE_CHANGED = "score_changed"
    DELETED = "deleted"


class MitigationStatus(str, Enum):
    """Mitigation action status enumeration."""
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    OVERDUE = "Overdue"
    COMPLETED = "Completed"


class AlertType(str, Enum):
    """Alert type enumeration."""
    HIGH_RISK = "HighRisk"
    FORENSIC_FLAG = "ForensicFlag"
    OVERDUE_MITIGATION = "OverdueMitigation"
    EMERGING_INSTITUTIONAL = "EmergingInstitutional"
    RISK_SUPPRESSION = "RiskSuppression"
    RISK_CHAIN_DETECTED = "RiskChainDetected"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class AlertRole(str, Enum):
    """Alert target role enumeration."""
    ALL = "all"
    EXECUTIVE = "executive"
    RISK_OFFICER = "risk_officer"
