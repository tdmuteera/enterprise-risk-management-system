"""
ERM Platform Database Architecture Documentation

This document describes the complete database schema for the Enterprise Risk Management platform.
All models use SQLAlchemy 2.x ORM with PostgreSQL UUID type and async support.
"""

# ============================================================================
# FILES & LOCATION
# ============================================================================

# Core Models:
#   models_complete.py          - Complete ORM model definitions
#   models_base.py              - Enumerations (legacy, use models_complete.py)

# Database Setup:
#   database.py                 - Async engine and session factory
#   config.py                   - Configuration (DB_URL, etc.)

# Migrations:
#   alembic_migration_001.py    - Initial schema migration
#   ALEMBIC_SETUP.md            - Migration instructions

# Data Seeding:
#   db_seed.py                  - Standalone seed script

# ============================================================================
# SCHEMA OVERVIEW
# ============================================================================

# 7 Main Tables:
# 1. departments           - University departments/faculties
# 2. users                 - System users with roles
# 3. risks                 - Risk register with scoring
# 4. risk_links            - Cross-department risk dependencies
# 5. risk_history          - Immutable audit log (append-only)
# 6. mitigation_actions    - Risk mitigation strategies
# 7. alerts                - System alerts and notifications

# ============================================================================
# TABLE: DEPARTMENTS
# ============================================================================

"""
Department or faculty in the university.

Fields:
  id (UUID PK)               - Primary key (PostgreSQL UUID)
  name (VARCHAR 255)         - Department name (unique, indexed)
  code (VARCHAR 4)           - 4-character code (unique, indexed)
  description (TEXT)         - Department description
  head_of_dept (VARCHAR 255) - Head of department name
  is_active (BOOLEAN)        - Active status (default: true)
  created_at (DATETIME)      - Created timestamp (auto-set)
  updated_at (DATETIME)      - Updated timestamp (auto-updated)

Indexes:
  - PK on id
  - UNIQUE on name
  - UNIQUE on code
  - INDEX on is_active

Sample Data:
  Finance (FIN), HR (HR), Academic Affairs (ACAD), IT (IT)
"""

# ============================================================================
# TABLE: USERS
# ============================================================================

"""
System user with role-based access control.

Fields:
  id (UUID PK)               - Primary key
  email (VARCHAR 255)        - Email (unique, indexed)
  hashed_password (VARCHAR)  - Bcrypt hashed password
  full_name (VARCHAR 255)    - Full name
  role (ENUM)                - User role:
                                 - admin: System administrator
                                 - risk_officer: Central risk management officer
                                 - dept_user: Department user
                                 - executive: University executive
  department_id (UUID FK)    - FK to departments (nullable)
  is_active (BOOLEAN)        - Active status (default: true)
  last_login (DATETIME)      - Last login timestamp
  created_at (DATETIME)      - Created timestamp
  updated_at (DATETIME)      - Updated timestamp

Indexes:
  - PK on id
  - UNIQUE on email
  - INDEX on role
  - INDEX on department_id
  - INDEX on is_active

Relationships:
  - Many Users in one Department
  - User can own many Risks
  - User can create many RiskLinks
  - User can be assigned MitigationActions
  - User appears in RiskHistory as changed_by

Sample Roles:
  - admin (1 user)
  - risk_officer (2 users)
  - dept_user (3 users, one per department)
  - executive (1 user)
"""

# ============================================================================
# TABLE: RISKS
# ============================================================================

"""
Risk register with multi-factor scoring.

Fields:
  id (UUID PK)                    - Primary key
  title (VARCHAR 255)            - Risk title (indexed)
  description (TEXT)             - Risk description
  category (ENUM)                - Risk category:
                                     Financial, HR, Academic, IT,
                                     Compliance, Operational, Reputational
  department_id (UUID FK)        - FK to departments (indexed)
  owner_id (UUID FK)             - FK to users (risk owner, indexed)
  
  # Scoring Factors (1-5 scale)
  likelihood (INT)               - Probability (1=very low, 5=very high)
  impact (INT)                   - Impact severity (1=negligible, 5=catastrophic)
  velocity (INT)                 - Speed of materialization (1=very slow, 5=immediate)
  detectability (INT)            - Detection difficulty (1=easy, 5=hard to detect)
  
  # Computed Score
  risk_score (FLOAT)             - Computed: likelihood × impact × velocity × detectability
                                   Range: 1.0 to 625.0
  
  status (ENUM)                  - Risk status:
                                     Open, In-Progress, Mitigated, Closed, Escalated
  institutional_risk_index (FLOAT) - Institution-wide risk aggregation
  
  created_at (DATETIME)          - Created timestamp
  updated_at (DATETIME)          - Updated timestamp

Constraints:
  - CHECK likelihood BETWEEN 1 AND 5
  - CHECK impact BETWEEN 1 AND 5
  - CHECK velocity BETWEEN 1 AND 5
  - CHECK detectability BETWEEN 1 AND 5

Indexes:
  - PK on id
  - INDEX on title
  - INDEX on category
  - INDEX on department_id
  - INDEX on owner_id
  - INDEX on status
  - COMPOSITE INDEX on (department_id, status)  ← For filtering
  - INDEX on risk_score DESC                    ← For sorting

Relationships:
  - Many Risks in one Department
  - One Risk owned by one User
  - Risk can have many RiskLinks (source and target)
  - Risk has many RiskHistory entries
  - Risk can have many MitigationActions
  - Risk can have many Alerts

Risk Score Calculation:
  risk_score = likelihood × impact × velocity × detectability
  
  Example:
    likelihood=3, impact=4, velocity=2, detectability=5
    risk_score = 3 × 4 × 2 × 5 = 120.0

Sample Data:
  10 risks distributed across Finance, HR, Academic, IT departments
  Various risk categories and status values
"""

# ============================================================================
# TABLE: RISK_LINKS
# ============================================================================

"""
Cross-department risk dependencies and relationships.

Fields:
  id (UUID PK)           - Primary key
  source_risk_id (UUID FK)  - Source risk
  target_risk_id (UUID FK)  - Target risk
  link_type (ENUM)       - Type of link:
                             causes, related_to, escalates, triggers
  weight (FLOAT)         - Interdependency strength (0.0-1.0)
  notes (TEXT)           - Notes on the relationship
  created_by_id (UUID FK)  - User who created the link
  created_at (DATETIME)  - Created timestamp

Indexes:
  - PK on id
  - INDEX on source_risk_id
  - INDEX on target_risk_id
  - INDEX on created_by_id

Relationships:
  - Many RiskLinks can link Risks
  - One User creates RiskLink

Example Links:
  1. Financial Risk → Governance Risk (link_type: causes, weight: 0.9)
  2. Student Data Breach → Cybersecurity Risk (link_type: related_to, weight: 0.8)
  3. Data Breach → Reputational Risk (link_type: escalates, weight: 0.95)
"""

# ============================================================================
# TABLE: RISK_HISTORY
# ============================================================================

"""
IMMUTABLE AUDIT LOG - APPEND-ONLY, NEVER UPDATED OR DELETED.

This table records every change to a risk for forensic analysis and audit trails.

Fields:
  id (UUID PK)           - Primary key
  risk_id (UUID FK)      - FK to risks (indexed)
  action (ENUM)          - Type of change:
                             created, updated, status_changed, score_changed, deleted
  changed_by_id (UUID FK)  - User who made the change
  changed_at (DATETIME)  - When the change occurred (auto-timestamped)
  previous_values (JSONB)  - JSON of values BEFORE change
  new_values (JSONB)     - JSON of values AFTER change
  ip_address (VARCHAR 45)  - IPv4 or IPv6 of user
  user_agent (VARCHAR 255) - Browser/client user agent

Indexes:
  - PK on id
  - INDEX on risk_id
  - INDEX on changed_by_id
  - INDEX on changed_at
  - INDEX on changed_at DESC  ← For reverse chronological queries

Important:
  - This table should NEVER be updated or deleted
  - Use INSERT-ONLY pattern
  - All changes must be logged here
  - Example audit trail entry:
    {
      risk_id: "uuid-123",
      action: "status_changed",
      changed_by: "user-456",
      changed_at: "2026-04-21 10:30:00",
      previous_values: {"status": "Open"},
      new_values: {"status": "In-Progress"},
      ip_address: "192.168.1.1",
      user_agent: "Mozilla/5.0..."
    }
"""

# ============================================================================
# TABLE: MITIGATION_ACTIONS
# ============================================================================

"""
Risk mitigation strategy and action tracking.

Fields:
  id (UUID PK)          - Primary key
  risk_id (UUID FK)     - FK to risks
  description (TEXT)    - Mitigation description
  assigned_to_id (UUID FK)  - User responsible for mitigation
  due_date (DATETIME)   - Target completion date
  completion_date (DATETIME)  - Actual completion (nullable)
  status (ENUM)         - Mitigation status:
                             Pending, In-Progress, Overdue, Completed
  effectiveness_score (INT)  - Score after completion (1-5, nullable)
  created_at (DATETIME) - Created timestamp
  updated_at (DATETIME) - Updated timestamp

Indexes:
  - PK on id
  - INDEX on risk_id
  - INDEX on assigned_to_id
  - INDEX on status

Relationships:
  - Many MitigationActions per Risk
  - One User assigned to each MitigationAction

Sample Data:
  Mitigation for Budget Overrun: "Implement strict budget approval"
  Mitigation for Data Breach: "Upgrade encryption protocols"
"""

# ============================================================================
# TABLE: ALERTS
# ============================================================================

"""
System alerts for risk escalations and forensic flags.

Fields:
  id (UUID PK)          - Primary key
  alert_type (ENUM)     - Type of alert:
                             HighRisk, ForensicFlag, OverdueMitigation,
                             EmergingInstitutional, RiskSuppression,
                             RiskChainDetected
  risk_id (UUID FK)     - FK to risks (nullable, some alerts are institutional)
  message (TEXT)        - Alert message
  severity (ENUM)       - Severity level:
                             Info, Warning, Critical
  is_read (BOOLEAN)     - Whether alert has been read
  is_dismissed (BOOLEAN)  - Whether alert has been dismissed
  created_for_role (ENUM) - Target role(s):
                             all, executive, risk_officer
  created_at (DATETIME) - Created timestamp

Indexes:
  - PK on id
  - INDEX on alert_type
  - INDEX on risk_id
  - INDEX on severity
  - INDEX on is_read
  - INDEX on created_at

Sample Alerts:
  1. HIGH_RISK: "Critical: Student data breach detected" (CRITICAL)
  2. OVERDUE_MITIGATION: "Budget risk mitigation approaching deadline" (WARNING)
  3. RISK_CHAIN_DETECTED: "Risk chain: Expenditure → Governance" (WARNING)
  4. EMERGING_INSTITUTIONAL: "Reputational damage risk emerging" (WARNING)
"""

# ============================================================================
# ENUMERATIONS
# ============================================================================

"""
All ENUM types used throughout the schema:

UserRole:
  - admin: System administrator
  - risk_officer: Central risk officer
  - dept_user: Department staff
  - executive: University executive

RiskCategory:
  - Financial: Financial risks
  - HR: Human resources risks
  - Academic: Academic program risks
  - IT: IT infrastructure risks
  - Compliance: Regulatory compliance risks
  - Operational: Operational risks
  - Reputational: Reputational risks

RiskStatus:
  - Open: New or reopened risk
  - In-Progress: Being addressed
  - Mitigated: Mitigation in place
  - Closed: Risk resolved
  - Escalated: Escalated to senior management

RiskLinkType:
  - causes: Source risk causes target risk
  - related_to: Risks are related but not causal
  - escalates: Source risk escalates to target risk
  - triggers: Source risk triggers target risk

RiskHistoryAction:
  - created: Risk created
  - updated: Risk updated
  - status_changed: Risk status changed
  - score_changed: Risk score recalculated
  - deleted: Risk deleted

MitigationStatus:
  - Pending: Not yet started
  - In-Progress: Currently being worked on
  - Overdue: Past due date
  - Completed: Mitigation completed

AlertType:
  - HighRisk: Risk score exceeded threshold
  - ForensicFlag: Forensic analysis flag
  - OverdueMitigation: Mitigation past due
  - EmergingInstitutional: Institutional-level risk
  - RiskSuppression: Risk suppression detected
  - RiskChainDetected: Risk chain identified

AlertSeverity:
  - Info: Informational
  - Warning: Warning level
  - Critical: Critical level

AlertRole:
  - all: For all roles
  - executive: For executives only
  - risk_officer: For risk officers only
"""

# ============================================================================
# INITIALIZATION & MIGRATION
# ============================================================================

"""
Step 1: Initialize Alembic (if not done)
  alembic init alembic

Step 2: Copy migration file
  Copy alembic_migration_001.py to alembic/versions/

Step 3: Update alembic/env.py
  import models_complete
  target_metadata = models_complete.Base.metadata

Step 4: Create initial revision
  alembic upgrade head

Step 5: Seed data
  python db_seed.py

Step 6: Verify
  psql -d erm_db -c "SELECT COUNT(*) FROM risks;"
"""

# ============================================================================
# KEY FEATURES
# ============================================================================

"""
✓ UUID Primary Keys: All tables use PostgreSQL UUID type
✓ Async Support: All models compatible with SQLAlchemy async
✓ Timestamps: Every table has created_at and updated_at
✓ CHECK Constraints: Risk factors bounded to 1-5 scale
✓ Composite Indexes: (department_id, status) for efficient filtering
✓ Audit Trail: Immutable RiskHistory table for forensics
✓ Relationships: Proper foreign keys and cascade settings
✓ JSONB Support: RiskHistory stores before/after values as JSON
✓ Enumerations: Type-safe ENUMs for all categorization
✓ Seed Data: 4 departments, 7 users, 10 risks, 3 mitigations, 4 alerts
"""

# ============================================================================
# SEED DATA SUMMARY
# ============================================================================

"""
Departments:    4
  - Finance (FIN)
  - HR (HR)
  - Academic (ACAD)
  - IT (IT)

Users:          7
  - 1 admin
  - 2 risk officers
  - 3 department users
  - 1 executive

Risks:          10
  - Financial: 2 (Budget Overrun, Irregular Expenditure)
  - HR: 2 (Staff Attrition, Payroll System Failure)
  - Academic: 3 (Accreditation, Student Data Breach, Reputational)
  - IT: 2 (Cyber Security, System Downtime)
  - Compliance: 1 (Governance Violation)

Risk Links:     3
  - Expenditure → Governance (causes)
  - Data Breach → Cybersecurity (related_to)
  - Data Breach → Reputation (escalates)

Mitigations:    3
  - Budget approval process
  - Encryption protocols
  - EDR threat detection

Alerts:         4
  - High-risk data breach
  - Overdue budget mitigation
  - Risk chain detected
  - Emerging institutional risk
"""
