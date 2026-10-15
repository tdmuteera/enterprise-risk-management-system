"""
Complete SQLAlchemy 2.x ORM models for ERM Platform.
UUIDs use SQLAlchemy ``Uuid`` (PostgreSQL + SQLite). JSON columns use ``JSON``.
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum,
    Integer,
    Float,
    ForeignKey,
    Text,
    CheckConstraint,
    UniqueConstraint,
    Index,
    JSON,
    func,
)
from sqlalchemy.types import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

# Portable across PostgreSQL and SQLite (dev)
GUID = Uuid(as_uuid=True)
from datetime import datetime
import uuid
from enum import Enum as PyEnum

# Base class for all models with timestamps
Base = declarative_base()


class BaseModel:
    """Mixin providing created_at and updated_at to all models."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


# ============================================================================
# ENUMERATIONS
# ============================================================================

class UserRole(str, PyEnum):
    """User role enumeration."""
    ADMIN = "admin"
    RISK_MANAGER = "risk_manager"
    RISK_OFFICER = "risk_officer"
    DEPARTMENT_HEAD = "department_head"
    DEPT_USER = "dept_user"
    DATA_CLERK = "data_clerk"
    RISK_CLERK = "risk_clerk"
    EXECUTIVE = "executive"


class RiskCategory(str, PyEnum):
    """Risk category enumeration."""
    FINANCIAL = "Financial"
    HR = "HR"
    ACADEMIC = "Academic"
    IT = "IT"
    COMPLIANCE = "Compliance"
    OPERATIONAL = "Operational"
    REPUTATIONAL = "Reputational"


class RiskStatus(str, PyEnum):
    """Risk status enumeration."""
    DRAFT = "Draft"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    OPEN = "Open"
    IN_PROGRESS = "In-Progress"
    MITIGATED = "Mitigated"
    CLOSED = "Closed"
    ESCALATED = "Escalated"


class RiskType(str, PyEnum):
    """Risk type enumeration (inherent vs residual)."""
    INHERENT = "Inherent"
    RESIDUAL = "Residual"


class RiskLinkType(str, PyEnum):
    """Risk link type enumeration."""
    CAUSES = "causes"
    RELATED_TO = "related_to"
    ESCALATES = "escalates"
    TRIGGERS = "triggers"


class RiskHistoryAction(str, PyEnum):
    """Risk history action enumeration."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    SCORE_CHANGED = "score_changed"
    VIEWED = "viewed"
    DELETED = "deleted"


class MitigationStatus(str, PyEnum):
    """Mitigation action status enumeration."""
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    OVERDUE = "Overdue"
    COMPLETED = "Completed"


class AlertType(str, PyEnum):
    """Alert type enumeration."""
    HIGH_RISK = "HighRisk"
    FORENSIC_FLAG = "ForensicFlag"
    OVERDUE_MITIGATION = "OverdueMitigation"
    EMERGING_INSTITUTIONAL = "EmergingInstitutional"
    RISK_SUPPRESSION = "RiskSuppression"
    RISK_CHAIN_DETECTED = "RiskChainDetected"


class AlertSeverity(str, PyEnum):
    """Alert severity enumeration."""
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class AlertRole(str, PyEnum):
    """Alert target role enumeration."""
    ALL = "all"
    EXECUTIVE = "executive"
    RISK_OFFICER = "risk_officer"


# ============================================================================
# DEPARTMENT MODEL
# ============================================================================

class Department(Base, BaseModel):
    """University department or faculty."""
    __tablename__ = "departments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    code = Column(String(4), nullable=False, unique=True, index=True)  # 4-char code
    description = Column(Text, nullable=True)
    head_of_dept = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    users = relationship("User", back_populates="department", foreign_keys="User.department_id")
    risks = relationship("Risk", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, code={self.code}, name={self.name})>"


# ============================================================================
# USER MODEL
# ============================================================================

class User(Base, BaseModel):
    """System user with role-based access control."""
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DEPT_USER, nullable=False, index=True)
    department_id = Column(GUID, ForeignKey("departments.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])
    owned_risks = relationship("Risk", back_populates="owner", foreign_keys="Risk.owner_id")
    created_risk_links = relationship("RiskLink", back_populates="created_by", foreign_keys="RiskLink.created_by_id")
    assigned_mitigations = relationship("MitigationAction", back_populates="assigned_to")
    risk_history = relationship("RiskHistory", back_populates="changed_by")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# ============================================================================
# RISK MODEL
# ============================================================================

class Risk(Base, BaseModel):
    """Enterprise risk with scoring and linkage."""
    __tablename__ = "risks"
    __table_args__ = (
        CheckConstraint("likelihood BETWEEN 1 AND 5", name="ck_risk_likelihood"),
        CheckConstraint("impact BETWEEN 1 AND 5", name="ck_risk_impact"),
        CheckConstraint("velocity BETWEEN 1 AND 5", name="ck_risk_velocity"),
        CheckConstraint("detectability BETWEEN 1 AND 5", name="ck_risk_detectability"),
        Index("idx_risk_dept_status", "department_id", "status"),
        Index("idx_risk_score_desc", "risk_score", mysql_length=None),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(Enum(RiskCategory), nullable=False, index=True)
    department_id = Column(GUID, ForeignKey("departments.id"), nullable=False, index=True)
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    
    # Risk scoring factors (1-5)
    likelihood = Column(Integer, nullable=False)  # 1=very low, 5=very high
    impact = Column(Integer, nullable=False)      # 1=negligible, 5=catastrophic
    velocity = Column(Integer, nullable=False)    # 1=very slow, 5=immediate
    detectability = Column(Integer, nullable=False)  # 1=very easy, 5=very hard to detect
    
    # Computed risk score: likelihood × impact × velocity × detectability
    risk_score = Column(Float, nullable=False, index=True)
    
    risk_type = Column(Enum(RiskType), default=RiskType.INHERENT, nullable=False, index=True)
    parent_risk_id = Column(GUID, ForeignKey("risks.id"), nullable=True, index=True)
    reviewer_id = Column(GUID, ForeignKey("users.id"), nullable=True, index=True)
    review_justification = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(Enum(RiskStatus), default=RiskStatus.OPEN, nullable=False, index=True)
    institutional_risk_index = Column(Float, nullable=True, index=True)

    # Relationships
    department = relationship("Department", back_populates="risks", foreign_keys=[department_id])
    owner = relationship("User", back_populates="owned_risks", foreign_keys=[owner_id])
    parent_risk = relationship("Risk", remote_side="Risk.id", backref="residual_risks", foreign_keys=[parent_risk_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    risk_links_source = relationship(
        "RiskLink",
        back_populates="source_risk",
        foreign_keys="RiskLink.source_risk_id"
    )
    risk_links_target = relationship(
        "RiskLink",
        back_populates="target_risk",
        foreign_keys="RiskLink.target_risk_id"
    )
    history = relationship("RiskHistory", back_populates="risk", cascade="all, delete-orphan")
    mitigations = relationship("MitigationAction", back_populates="risk")
    alerts = relationship("Alert", back_populates="risk")

    def compute_risk_score(self) -> float:
        """Compute risk score from components."""
        return float(self.likelihood * self.impact * self.velocity * self.detectability)

    def __repr__(self) -> str:
        return f"<Risk(id={self.id}, title={self.title}, score={self.risk_score})>"


# ============================================================================
# RISK LINK MODEL (Cross-Department Linkage)
# ============================================================================

class RiskLink(Base):
    """Links between related risks (cross-department interdependencies)."""
    __tablename__ = "risk_links"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    source_risk_id = Column(GUID, ForeignKey("risks.id"), nullable=False, index=True)
    target_risk_id = Column(GUID, ForeignKey("risks.id"), nullable=False, index=True)
    link_type = Column(Enum(RiskLinkType), nullable=False)
    weight = Column(Float, nullable=False)  # 0.0-1.0: interdependency strength
    notes = Column(Text, nullable=True)
    created_by_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    source_risk = relationship("Risk", back_populates="risk_links_source", foreign_keys=[source_risk_id])
    target_risk = relationship("Risk", back_populates="risk_links_target", foreign_keys=[target_risk_id])
    created_by = relationship("User", back_populates="created_risk_links")

    def __repr__(self) -> str:
        return f"<RiskLink(id={self.id}, type={self.link_type}, weight={self.weight})>"


# ============================================================================
# RISK HISTORY MODEL (Immutable Audit Log)
# ============================================================================

class RiskHistory(Base):
    """
    Immutable audit trail for all risk changes.
    NEVER updated or deleted - append-only log.
    """
    __tablename__ = "risk_history"
    __table_args__ = (
        Index("idx_risk_history_changed_at_desc", "changed_at", mysql_length=None),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    risk_id = Column(GUID, ForeignKey("risks.id"), nullable=False, index=True)
    action = Column(Enum(RiskHistoryAction), nullable=False)
    changed_by_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    previous_values = Column(JSON, nullable=True)  # JSON stored values before change
    new_values = Column(JSON, nullable=True)       # JSON stored values after change
    
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(255), nullable=True)

    # Relationships
    risk = relationship("Risk", back_populates="history", foreign_keys=[risk_id])
    changed_by = relationship("User", back_populates="risk_history")

    def __repr__(self) -> str:
        return f"<RiskHistory(id={self.id}, risk_id={self.risk_id}, action={self.action})>"


class RiskHistoryArchive(Base):
    """
    Cold storage for risk_history rows moved by the scheduled archiver.
    Same shape as RiskHistory plus archived_at (no FK to risks to allow long-term retention).
    """

    __tablename__ = "risk_history_archive"
    __table_args__ = (Index("idx_risk_history_archive_changed_at", "changed_at"),)

    id = Column(GUID, primary_key=True, index=True)
    risk_id = Column(GUID, nullable=False, index=True)
    action = Column(Enum(RiskHistoryAction), nullable=False)
    changed_by_id = Column(GUID, nullable=False, index=True)
    changed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    previous_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    archived_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<RiskHistoryArchive(id={self.id}, risk_id={self.risk_id}, archived_at={self.archived_at})>"


# ============================================================================
# MITIGATION ACTION MODEL
# ============================================================================

class MitigationAction(Base, BaseModel):
    """Mitigation strategy and action tracking."""
    __tablename__ = "mitigation_actions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    risk_id = Column(GUID, ForeignKey("risks.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    assigned_to_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    
    due_date = Column(DateTime(timezone=True), nullable=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(Enum(MitigationStatus), default=MitigationStatus.PENDING, nullable=False, index=True)
    effectiveness_score = Column(Integer, nullable=True)  # 1-5 after completion

    # Relationships
    risk = relationship("Risk", back_populates="mitigations")
    assigned_to = relationship("User", back_populates="assigned_mitigations")

    def __repr__(self) -> str:
        return f"<MitigationAction(id={self.id}, risk_id={self.risk_id}, status={self.status})>"


# ============================================================================
# ALERT MODEL
# ============================================================================

class Alert(Base):
    """System alerts for risk escalations and forensic flags."""
    __tablename__ = "alerts"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    risk_id = Column(GUID, ForeignKey("risks.id"), nullable=True, index=True)

    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.INFO, nullable=False, index=True)

    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_dismissed = Column(Boolean, default=False, nullable=False)

    created_for_role = Column(Enum(AlertRole), default=AlertRole.ALL, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    risk = relationship("Risk", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity})>"


# ============================================================================
# SECURITY EVENT MODEL (Failed Login / Auth Forensics)
# ============================================================================

class SecurityEvent(Base):
    """Security events for auth forensics (e.g., failed login attempts)."""

    __tablename__ = "security_events"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    email_attempted = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    reason = Column(String(255), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<SecurityEvent(id={self.id}, email={self.email_attempted}, reason={self.reason})>"


# ============================================================================
# DOMAIN AUDIT EVENT MODEL (Generic Immutable Audit Log)
# ============================================================================

class DomainAuditEvent(Base):
    """Immutable audit log for non-risk domain entities (departments, users, alerts, mitigations)."""

    __tablename__ = "domain_audit_events"
    __table_args__ = (
        Index("idx_domain_audit_changed_at_desc", "changed_at", mysql_length=None),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)

    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(GUID, nullable=False, index=True)

    action = Column(String(50), nullable=False, index=True)
    changed_by_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)

    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    previous_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

    changed_by = relationship("User")

    def __repr__(self) -> str:
        return f"<DomainAuditEvent(id={self.id}, entity_type={self.entity_type}, action={self.action})>"
