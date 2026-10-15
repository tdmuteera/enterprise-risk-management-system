"""
Comprehensive ORM models for ERM Platform.
These models will be split into separate files during full development.
Currently provided as stubs for project initialization.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Float, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
import enum
from database import Base


# ============================================================================
# Enumerations
# ============================================================================

class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    RISK_OFFICER = "risk_officer"
    DEPARTMENT_HEAD = "department_head"
    AUDITOR = "auditor"
    VIEWER = "viewer"


class RiskSeverity(str, enum.Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskStatus(str, enum.Enum):
    """Risk status enumeration."""
    NEW = "new"
    ACTIVE = "active"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class MitigationStatus(str, enum.Enum):
    """Mitigation strategy status."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class AlertType(str, enum.Enum):
    """Alert type enumeration."""
    RISK_ESCALATION = "risk_escalation"
    MITIGATION_DUE = "mitigation_due"
    POLICY_VIOLATION = "policy_violation"
    AUDIT_ALERT = "audit_alert"
    SYSTEM_ALERT = "system_alert"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# ============================================================================
# User Model
# ============================================================================

class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    department_id = Column(Integer, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


# ============================================================================
# Department Model
# ============================================================================

class Department(Base):
    """Department/Faculty model."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    head_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name={self.name}, code={self.code})>"


# ============================================================================
# Risk Model
# ============================================================================

class Risk(Base):
    """Risk register model."""
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    risk_category = Column(String(100), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    severity = Column(Enum(RiskSeverity), default=RiskSeverity.MEDIUM, nullable=False)
    status = Column(Enum(RiskStatus), default=RiskStatus.NEW, nullable=False, index=True)
    
    likelihood_score = Column(Float, nullable=True)
    impact_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True, index=True)
    
    identified_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    review_date = Column(DateTime, nullable=True)
    
    evidence_files = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Risk(id={self.id}, title={self.title}, severity={self.severity})>"


# ============================================================================
# Risk Link Model (relationship between risks)
# ============================================================================

class RiskLink(Base):
    """Model for linking related risks."""
    __tablename__ = "risk_links"

    id = Column(Integer, primary_key=True, index=True)
    source_risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False, index=True)
    target_risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False, index=True)
    link_type = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<RiskLink(source={self.source_risk_id}, target={self.target_risk_id})>"


# ============================================================================
# Risk History Model (audit trail)
# ============================================================================

class RiskHistory(Base):
    """Audit trail for risk changes."""
    __tablename__ = "risk_history"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False, index=True)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    action = Column(String(100), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<RiskHistory(risk_id={self.risk_id}, action={self.action})>"


# ============================================================================
# Mitigation Model
# ============================================================================

class Mitigation(Base):
    """Risk mitigation strategy model."""
    __tablename__ = "mitigations"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(MitigationStatus), default=MitigationStatus.PLANNED, nullable=False)
    
    target_completion_date = Column(DateTime, nullable=False)
    actual_completion_date = Column(DateTime, nullable=True)
    
    budget_allocated = Column(Float, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Mitigation(id={self.id}, risk_id={self.risk_id}, status={self.status})>"


# ============================================================================
# Alert Model
# ============================================================================

class Alert(Base):
    """System alerts for risk escalations and milestones."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(RiskSeverity), default=RiskSeverity.MEDIUM, nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING, nullable=False, index=True)
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    due_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type}, status={self.status})>"
