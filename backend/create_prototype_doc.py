"""
Script to generate detailed ERM Prototype Documentation as a Word document.
"""

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# ==================== STYLES ====================
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)

# ==================== TITLE PAGE ====================
title = doc.add_heading('ENTERPRISE RISK MANAGEMENT (ERM) PLATFORM', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph('Intelligent Risk Management System for Zimbabwean Universities')
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in subtitle.runs:
    run.bold = True
    run.font.size = Pt(14)

doc.add_paragraph()

proto_title = doc.add_paragraph('PROTOTYPE DOCUMENTATION')
proto_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in proto_title.runs:
    run.bold = True
    run.font.size = Pt(16)

doc.add_paragraph()
doc.add_paragraph()

info_para = doc.add_paragraph()
info_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
info_para.add_run('Version: ').bold = True
info_para.add_run('1.0.0')
doc.add_paragraph()
info2 = doc.add_paragraph()
info2.alignment = WD_ALIGN_PARAGRAPH.CENTER
info2.add_run('Date: ').bold = True
info2.add_run('May 2026')
doc.add_paragraph()
info3 = doc.add_paragraph()
info3.alignment = WD_ALIGN_PARAGRAPH.CENTER
info3.add_run('Document Type: ').bold = True
info3.add_run('System Prototype Specification')

doc.add_page_break()

# ==================== TABLE OF CONTENTS ====================
doc.add_heading('TABLE OF CONTENTS', level=1)
toc_items = [
    '1. Introduction',
    '   1.1 Purpose of the Document',
    '   1.2 Scope of the Prototype',
    '   1.3 Target Audience',
    '2. System Overview',
    '   2.1 Problem Statement',
    '   2.2 Proposed Solution',
    '   2.3 System Architecture',
    '3. Prototype Objectives',
    '4. Technology Stack',
    '   4.1 Backend Technologies',
    '   4.2 Frontend Technologies',
    '   4.3 Database and Infrastructure',
    '5. System Features',
    '   5.1 User Authentication and Authorization',
    '   5.2 Risk Management Module',
    '   5.3 Mitigation Tracking',
    '   5.4 Alert System',
    '   5.5 Dashboard and Analytics',
    '   5.6 Audit Trail and Forensics',
    '   5.7 Reporting Module',
    '6. Data Model',
    '   6.1 Core Entities',
    '   6.2 Entity Relationships',
    '7. User Roles and Permissions',
    '8. User Interface Design',
    '9. API Endpoints',
    '10. Security Features',
    '11. Prototype Limitations',
    '12. Installation and Setup',
    '13. Future Enhancements',
    '14. Conclusion',
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)

doc.add_page_break()

# ==================== 1. INTRODUCTION ====================
doc.add_heading('1. Introduction', level=1)

doc.add_heading('1.1 Purpose of the Document', level=2)
doc.add_paragraph(
    'This document provides a comprehensive description of the Enterprise Risk Management (ERM) Platform prototype. '
    'It serves as a technical specification and user guide for stakeholders, developers, and evaluators to understand '
    "the system's capabilities, architecture, and implementation details. The document outlines the functional "
    'requirements, system design, and the rationale behind key technical decisions.'
)

doc.add_heading('1.2 Scope of the Prototype', level=2)
doc.add_paragraph(
    'The prototype demonstrates a full-stack web application designed to support enterprise risk management '
    'processes within Zimbabwean universities. It encompasses:'
)
scope_items = [
    'A RESTful API backend built with FastAPI for handling business logic and data persistence',
    'A responsive React-based single-page application (SPA) for user interaction',
    'JWT-based authentication with role-based access control (RBAC)',
    'Complete risk lifecycle management from identification to resolution',
    'Mitigation strategy tracking and effectiveness monitoring',
    'Automated alert generation for risk escalations and due dates',
    'Multi-level dashboards for different organizational perspectives',
    'Comprehensive audit trail and forensic analysis capabilities',
    'Report generation functionality for compliance and governance',
]
for item in scope_items:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('1.3 Target Audience', level=2)
doc.add_paragraph('This document is intended for:')
audience = [
    'University administrators and risk management officers',
    'Department heads responsible for risk oversight',
    'IT staff responsible for system deployment and maintenance',
    'Academic supervisors evaluating the dissertation project',
    'Future developers who may extend or maintain the system',
]
for item in audience:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ==================== 2. SYSTEM OVERVIEW ====================
doc.add_heading('2. System Overview', level=1)

doc.add_heading('2.1 Problem Statement', level=2)
doc.add_paragraph(
    'Zimbabwean universities face significant challenges in managing institutional risks effectively. '
    'Current risk management practices often rely on manual processes, spreadsheets, and fragmented systems '
    'that lead to:'
)
problems = [
    'Inconsistent risk identification and assessment across departments',
    'Delayed response to emerging risks due to poor communication channels',
    'Lack of visibility into enterprise-wide risk exposure',
    'Insufficient audit trails for regulatory compliance',
    'Difficulty in tracking mitigation progress and effectiveness',
    'Limited ability to detect suspicious patterns or anomalies in risk reporting',
]
for item in problems:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('2.2 Proposed Solution', level=2)
doc.add_paragraph(
    'The ERM Platform addresses these challenges by providing an integrated, web-based solution that:'
)
solutions = [
    'Centralises risk data in a secure, accessible repository',
    'Standardises risk assessment using configurable scoring matrices',
    'Enables real-time collaboration between stakeholders',
    'Automates alert generation for critical events',
    'Provides role-appropriate dashboards and reports',
    'Maintains complete audit trails for accountability',
    'Offers forensic tools to detect anomalies and suspicious patterns',
]
for item in solutions:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('2.3 System Architecture', level=2)
doc.add_paragraph(
    'The system follows a modern client-server architecture with clear separation of concerns:'
)
doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Frontend (Client Layer): ').bold = True
p.add_run("A React single-page application running in the user's browser, responsible for rendering the user interface, "
          'managing local state, and communicating with the backend via HTTP/REST.')
doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Backend (Application Layer): ').bold = True
p.add_run('A FastAPI-based REST API server that handles authentication, business logic, data validation, '
          'and orchestrates database operations. It exposes documented endpoints via OpenAPI/Swagger.')
doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Database (Data Layer): ').bold = True
p.add_run('PostgreSQL (production) or SQLite (development) for persistent storage of all application data '
          'including users, departments, risks, mitigations, alerts, and audit logs.')

doc.add_paragraph()
doc.add_paragraph('The architecture supports:')
arch_features = [
    'Horizontal scalability through stateless API design',
    'Asynchronous request handling for improved performance',
    'Database connection pooling for efficient resource utilisation',
    'Docker containerisation for consistent deployment',
]
for item in arch_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ==================== 3. PROTOTYPE OBJECTIVES ====================
doc.add_heading('3. Prototype Objectives', level=1)

doc.add_paragraph(
    'The following objectives guide the development and evaluation of this prototype:'
)
doc.add_paragraph()

objectives = [
    ('To demonstrate end-to-end connectivity', 'Establish seamless communication between the React frontend and FastAPI backend through a well-documented REST API.'),
    ('To implement secure authentication', 'Provide JWT-based login with role-based access control ensuring users can only access features appropriate to their role.'),
    ('To enable risk registration', 'Allow users to create, view, update, and archive risks in a centralised register with standardised data entry.'),
    ('To calculate risk scores', 'Implement a multi-factor scoring algorithm considering likelihood, impact, velocity, and detectability.'),
    ('To track mitigation strategies', 'Link mitigation actions to specific risks and monitor their progress from planning through completion.'),
    ('To generate automated alerts', 'Trigger notifications when risks escalate, mitigations are due, or anomalies are detected.'),
    ('To provide role-appropriate dashboards', 'Deliver department-level, cross-department, and executive views with relevant key performance indicators.'),
    ('To maintain audit trails', 'Record all changes to risk records with timestamps, user identification, and before/after values for accountability.'),
    ('To support forensic analysis', 'Detect suspicious patterns such as score suppressions, chronic unresolved risks, and sudden closures.'),
    ('To enable compliance reporting', 'Generate reports in PDF and Excel formats suitable for governance committees and regulatory bodies.'),
]

for i, (title, desc) in enumerate(objectives, 1):
    p = doc.add_paragraph()
    p.add_run(f'{i}. {title}: ').bold = True
    p.add_run(desc)

doc.add_page_break()

# ==================== 4. TECHNOLOGY STACK ====================
doc.add_heading('4. Technology Stack', level=1)

doc.add_heading('4.1 Backend Technologies', level=2)

backend_table = doc.add_table(rows=1, cols=3)
backend_table.style = 'Table Grid'
hdr = backend_table.rows[0].cells
hdr[0].text = 'Technology'
hdr[1].text = 'Version'
hdr[2].text = 'Purpose'
for cell in hdr:
    cell.paragraphs[0].runs[0].bold = True

backend_data = [
    ('FastAPI', '0.104+', 'High-performance async web framework for building APIs'),
    ('Uvicorn', 'Latest', 'ASGI server for running the FastAPI application'),
    ('SQLAlchemy', '2.x', 'Async ORM for database operations and model definitions'),
    ('asyncpg', 'Latest', 'High-performance async PostgreSQL driver'),
    ('Pydantic', 'v2', 'Data validation and settings management'),
    ('Python-jose', 'Latest', 'JWT token generation and validation'),
    ('Passlib + bcrypt', 'Latest', 'Secure password hashing'),
    ('APScheduler', 'Latest', 'Background task scheduling for alerts'),
    ('ReportLab', 'Latest', 'PDF report generation'),
    ('openpyxl', 'Latest', 'Excel report generation'),
    ('Alembic', 'Latest', 'Database schema migrations'),
    ('Pytest', 'Latest', 'Testing framework with async support'),
]

for tech, ver, purpose in backend_data:
    row = backend_table.add_row().cells
    row[0].text = tech
    row[1].text = ver
    row[2].text = purpose

doc.add_paragraph()

doc.add_heading('4.2 Frontend Technologies', level=2)

frontend_table = doc.add_table(rows=1, cols=3)
frontend_table.style = 'Table Grid'
hdr = frontend_table.rows[0].cells
hdr[0].text = 'Technology'
hdr[1].text = 'Version'
hdr[2].text = 'Purpose'
for cell in hdr:
    cell.paragraphs[0].runs[0].bold = True

frontend_data = [
    ('React', '18.3+', 'Component-based UI library'),
    ('TypeScript', '5.3+', 'Type-safe JavaScript for better developer experience'),
    ('Vite', '5.0+', 'Fast build tool and development server'),
    ('React Router', '6.22+', 'Client-side routing and navigation'),
    ('TanStack Query', '5.28+', 'Server state management and caching'),
    ('Axios', '1.6+', 'HTTP client for API communication'),
    ('React Hook Form', '7.50+', 'Performant form handling'),
    ('Zod', '3.22+', 'Schema validation for forms'),
    ('Tailwind CSS', '3.4+', 'Utility-first CSS framework'),
    ('Recharts', '2.12+', 'Data visualisation library'),
    ('Lucide React', 'Latest', 'Icon library'),
    ('date-fns', '3.3+', 'Date manipulation utilities'),
]

for tech, ver, purpose in frontend_data:
    row = frontend_table.add_row().cells
    row[0].text = tech
    row[1].text = ver
    row[2].text = purpose

doc.add_paragraph()

doc.add_heading('4.3 Database and Infrastructure', level=2)

infra_items = [
    ('PostgreSQL 13+', 'Production database with full ACID compliance'),
    ('SQLite', 'Development database for rapid prototyping'),
    ('Docker', 'Containerisation for consistent deployment'),
    ('Docker Compose', 'Multi-container orchestration'),
]

for tech, purpose in infra_items:
    p = doc.add_paragraph()
    p.add_run(f'{tech}: ').bold = True
    p.add_run(purpose)

doc.add_page_break()

# ==================== 5. SYSTEM FEATURES ====================
doc.add_heading('5. System Features', level=1)

doc.add_heading('5.1 User Authentication and Authorization', level=2)
doc.add_paragraph(
    'The system implements a comprehensive authentication and authorisation system:'
)
auth_features = [
    'JWT (JSON Web Token) based authentication with configurable token expiry (default: 8 hours access, 30 days refresh)',
    'Secure password hashing using bcrypt algorithm',
    'Role-based access control (RBAC) with nine defined roles',
    'Protected routes that redirect unauthenticated users to login',
    'Session persistence using browser localStorage',
    'Automatic session expiry handling with user notification',
    'Registration flow with optional department assignment',
]
for item in auth_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.2 Risk Management Module', level=2)
doc.add_paragraph('The core risk management functionality includes:')
risk_features = [
    'Risk creation with mandatory fields: title, description, category, department, owner',
    'Multi-factor scoring: Likelihood (1-5), Impact (1-5), Velocity (1-5), Detectability (1-5)',
    'Automatic normalised score calculation and colour band assignment (Critical/High/Medium/Low)',
    'Risk status workflow: Draft -> Open -> In-Progress/Escalated -> Mitigated -> Closed',
    'Approval workflow for department-level users (Pending Approval -> Approved/Rejected)',
    'Risk categories: Financial, HR, Academic, IT, Compliance, Operational, Reputational',
    'Risk linking to identify related/dependent risks',
    'Interactive risk heatmap visualisation (Likelihood x Impact matrix)',
    'Risk filtering, sorting, and pagination',
    'Inline audit trail showing change history per risk',
]
for item in risk_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.3 Mitigation Tracking', level=2)
doc.add_paragraph('Mitigation management capabilities:')
mit_features = [
    'Link multiple mitigations to a single risk',
    'Track mitigation status: Not Started, In Progress, Completed',
    'Assign mitigation owner and due date',
    'Record effectiveness score (1-100%)',
    'Budget allocation tracking',
    'Automatic alerts for overdue mitigations',
]
for item in mit_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.4 Alert System', level=2)
doc.add_paragraph('Automated alerting capabilities:')
alert_features = [
    'Risk escalation alerts when severity increases',
    'Mitigation due date reminders',
    'Policy violation notifications',
    'Audit alerts for suspicious activity',
    'System alerts for maintenance events',
    'Alert status workflow: Pending -> Acknowledged -> Resolved/Dismissed',
    'Bell icon notification with unread count in navigation bar',
    'Alert severity colour coding',
]
for item in alert_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.5 Dashboard and Analytics', level=2)
doc.add_paragraph('The system provides three dashboard levels:')

p = doc.add_paragraph()
p.add_run('Department Dashboard: ').bold = True
p.add_run('Shows risks specific to a single department with KPIs for total risks, critical count, average score, and open mitigations.')
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run('Cross-Department Dashboard: ').bold = True
p.add_run('Provides a comparative view across multiple departments for risk officers and managers.')
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run('Executive Dashboard: ').bold = True
p.add_run('Offers institution-wide summary with high-level KPIs, distribution charts, and trend analysis.')
doc.add_paragraph()

doc.add_paragraph('Analytics features include:')
analytics_features = [
    'Real-time KPI cards (Total Risks, Critical Count, Average Score)',
    'Risk distribution by severity level',
    'Trend analysis showing risk counts over time',
    'Interactive risk heatmap',
    'Department comparison charts',
]
for item in analytics_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.6 Audit Trail and Forensics', level=2)
doc.add_paragraph('Comprehensive auditing capabilities:')
audit_features = [
    'Complete change history for all risk records',
    'Captures: action type, timestamp, user, IP address, previous values, new values',
    'Searchable and filterable audit log interface',
    'Expandable rows to view detailed before/after comparisons',
    'Export to CSV for external analysis',
    'Pagination for large audit datasets',
]
for item in audit_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph()
doc.add_paragraph('Forensic Panel features (for risk officers and admins):')
forensic_features = [
    'Score Suppression Detection: Identifies suspicious score drops near reporting deadlines',
    'Chronic Unresolved Risks: Lists risks open for 90+ days with minimal action',
    'Risk Chain Network: Visualises relationships between linked risks',
    'Anomaly Feed: Real-time feed of flagged suspicious events',
    'Investigation Actions: Quick links to drill down into specific risks',
]
for item in forensic_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_heading('5.7 Reporting Module', level=2)
doc.add_paragraph('Report generation capabilities:')
report_features = [
    'Risk register reports with current status and scores',
    'Department-specific reports',
    'Executive summary reports',
    'Compliance reports for regulatory requirements',
    'Export formats: PDF, Excel, JSON',
    'Configurable report parameters (date range, department, status)',
]
for item in report_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ==================== 6. DATA MODEL ====================
doc.add_heading('6. Data Model', level=1)

doc.add_heading('6.1 Core Entities', level=2)

p = doc.add_paragraph()
p.add_run('User Entity').bold = True
doc.add_paragraph('Stores user account information and authentication credentials.')
user_fields = [
    'id (Primary Key), username, email, full_name, hashed_password',
    'role (Enum: admin, risk_officer, department_head, auditor, viewer, etc.)',
    'department_id (Foreign Key to Department)',
    'is_active, is_verified, created_at, updated_at, last_login',
]
for f in user_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Department Entity').bold = True
doc.add_paragraph('Represents university faculties and administrative units.')
dept_fields = [
    'id (Primary Key), name, code (unique identifier)',
    'description, head_id (FK to User)',
    'is_active, created_at, updated_at',
]
for f in dept_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Risk Entity').bold = True
doc.add_paragraph('Central entity for risk register entries.')
risk_fields = [
    'id (Primary Key), title, description, risk_category',
    'department_id (FK), owner_id (FK to User)',
    'severity (Enum: critical, high, medium, low)',
    'status (Enum: new, active, mitigating, resolved, archived)',
    'likelihood_score, impact_score, overall_score (calculated)',
    'identified_date, due_date, review_date',
    'evidence_files (JSON), tags (JSON)',
    'created_at, updated_at',
]
for f in risk_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Risk Link Entity').bold = True
doc.add_paragraph('Captures relationships between risks.')
link_fields = [
    'id, source_risk_id (FK), target_risk_id (FK)',
    'link_type (e.g., "causes", "depends_on", "related_to")',
    'notes, created_at',
]
for f in link_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Risk History Entity').bold = True
doc.add_paragraph('Audit trail for risk changes.')
history_fields = [
    'id, risk_id (FK), changed_by_id (FK to User)',
    'action (e.g., CREATE, UPDATE, DELETE)',
    'old_values (JSON), new_values (JSON)',
    'notes, created_at',
]
for f in history_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Mitigation Entity').bold = True
doc.add_paragraph('Tracks risk mitigation strategies.')
mit_fields = [
    'id, risk_id (FK), title, description',
    'owner_id (FK), status (Enum: planned, in_progress, completed, on_hold, cancelled)',
    'target_completion_date, actual_completion_date',
    'budget_allocated, effectiveness_score',
    'created_at, updated_at',
]
for f in mit_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Alert Entity').bold = True
doc.add_paragraph('System alerts and notifications.')
alert_fields = [
    'id, alert_type (Enum: risk_escalation, mitigation_due, policy_violation, audit_alert, system_alert)',
    'risk_id (FK, optional), title, message',
    'severity, status (Enum: pending, acknowledged, resolved, dismissed)',
    'assigned_to_id, acknowledged_by_id, acknowledged_at',
    'due_date, created_at, updated_at',
]
for f in alert_fields:
    doc.add_paragraph(f, style='List Bullet')

doc.add_heading('6.2 Entity Relationships', level=2)
relationships = [
    'User belongs to one Department (optional); Department has many Users',
    'Department has many Risks; Risk belongs to one Department',
    'Risk has one Owner (User); User can own many Risks',
    'Risk has many Mitigations; Mitigation belongs to one Risk',
    'Risk has many RiskHistory entries for audit trail',
    'Risk can be linked to many other Risks through RiskLink',
    'Alert may reference one Risk; Risk can have many Alerts',
]
for r in relationships:
    doc.add_paragraph(r, style='List Bullet')

doc.add_page_break()

# ==================== 7. USER ROLES ====================
doc.add_heading('7. User Roles and Permissions', level=1)

roles_table = doc.add_table(rows=1, cols=3)
roles_table.style = 'Table Grid'
hdr = roles_table.rows[0].cells
hdr[0].text = 'Role'
hdr[1].text = 'Dashboard Access'
hdr[2].text = 'Capabilities'
for cell in hdr:
    cell.paragraphs[0].runs[0].bold = True

roles_data = [
    ('Admin', 'All dashboards', 'Full system access, user management, configuration'),
    ('Risk Officer', 'Cross-dept & Executive', 'Manage all risks, approve/reject, forensic panel'),
    ('Risk Manager', 'Cross-dept & Executive', 'Oversee risk portfolio, generate reports'),
    ('Department Head', 'Department specific', 'Approve department risks, view department analytics'),
    ('Risk Clerk', 'Department specific', 'Create/edit risks (require approval), view department data'),
    ('Data Clerk', 'Department specific', 'Data entry for risks, limited editing'),
    ('Dept User', 'Department specific', 'Create risks (require approval), view own department'),
    ('Executive', 'Executive dashboard', 'View-only access to high-level summaries'),
    ('Viewer', 'Limited', 'Read-only access to assigned areas'),
    ('Auditor', 'Audit trail', 'Access audit logs and history'),
]

for role, dash, caps in roles_data:
    row = roles_table.add_row().cells
    row[0].text = role
    row[1].text = dash
    row[2].text = caps

doc.add_page_break()

# ==================== 8. USER INTERFACE ====================
doc.add_heading('8. User Interface Design', level=1)

doc.add_paragraph('The frontend follows modern UI/UX principles:')
ui_features = [
    'Responsive design adapting to desktop, tablet, and mobile screens',
    'Consistent navigation with collapsible sidebar',
    'Clean, professional colour scheme with risk-level colour coding',
    'Card-based layout for data presentation',
    'Interactive data tables with sorting, filtering, and pagination',
    'Form validation with real-time feedback',
    'Loading spinners and skeleton screens for better perceived performance',
    'Toast notifications for user feedback',
    'Breadcrumb navigation for complex workflows',
]
for item in ui_features:
    doc.add_paragraph(item, style='List Bullet')

doc.add_paragraph()
doc.add_paragraph('Key screens include:')
screens = [
    'Login / Registration pages',
    'Dashboard views (Department, Cross-Department, Executive)',
    'Risk List with filtering and search',
    'Risk Detail view with linked risks and audit trail',
    'Risk Create/Edit form with live score preview',
    'Alerts page with notification management',
    'Audit Trail page with expandable change details',
    'Forensic Panel for anomaly detection',
    'Reports page for generating exports',
    'Settings and User Management pages',
]
for s in screens:
    doc.add_paragraph(s, style='List Bullet')

doc.add_page_break()

# ==================== 9. API ENDPOINTS ====================
doc.add_heading('9. API Endpoints', level=1)

doc.add_paragraph('The backend exposes RESTful endpoints organised by domain:')
doc.add_paragraph()

p = doc.add_paragraph()
p.add_run('Authentication Endpoints').bold = True
auth_endpoints = [
    'POST /api/v1/auth/register - User registration',
    'POST /api/v1/auth/login - User login (returns JWT)',
    'POST /api/v1/auth/refresh - Refresh access token',
    'POST /api/v1/auth/logout - User logout',
]
for e in auth_endpoints:
    doc.add_paragraph(e, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Risk Endpoints').bold = True
risk_endpoints = [
    'GET /api/v1/risks - List risks (with pagination, filtering, sorting)',
    'POST /api/v1/risks - Create new risk',
    'GET /api/v1/risks/{id} - Get risk details with linked risks and audit trail',
    'PATCH /api/v1/risks/{id} - Update risk',
    'DELETE /api/v1/risks/{id} - Archive risk',
    'POST /api/v1/risks/{id}/approve - Approve pending risk',
    'POST /api/v1/risks/{id}/reject - Reject pending risk',
]
for e in risk_endpoints:
    doc.add_paragraph(e, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Department Endpoints').bold = True
dept_endpoints = [
    'GET /api/v1/departments - List all departments',
    'GET /api/v1/departments/{id} - Get department details',
    'GET /api/v1/departments/{id}/risks - Get risks for department',
]
for e in dept_endpoints:
    doc.add_paragraph(e, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Analytics Endpoints').bold = True
analytics_endpoints = [
    'GET /api/v1/analytics/institutional-summary - Enterprise-wide statistics',
    'GET /api/v1/analytics/trend - Risk trend data over time',
]
for e in analytics_endpoints:
    doc.add_paragraph(e, style='List Bullet')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Audit Endpoints').bold = True
audit_endpoints = [
    'GET /api/v1/audit-logs - List audit entries with filters',
]
for e in audit_endpoints:
    doc.add_paragraph(e, style='List Bullet')

doc.add_page_break()

# ==================== 10. SECURITY FEATURES ====================
doc.add_heading('10. Security Features', level=1)

security_features = [
    ('Password Security', 'Passwords are hashed using bcrypt with automatic salting, never stored in plain text.'),
    ('JWT Authentication', 'Stateless authentication using signed tokens with configurable expiry.'),
    ('RBAC', 'Role-based access control enforced at both API and UI levels.'),
    ('CORS Protection', 'Cross-Origin Resource Sharing configured to allow only trusted origins.'),
    ('SQL Injection Prevention', 'SQLAlchemy ORM with parameterised queries prevents injection attacks.'),
    ('Input Validation', 'Pydantic schemas validate all incoming data before processing.'),
    ('Audit Logging', 'All changes are logged with user identity and timestamp.'),
    ('Environment Variables', 'Sensitive configuration stored in environment variables, not code.'),
]

for title, desc in security_features:
    p = doc.add_paragraph()
    p.add_run(f'{title}: ').bold = True
    p.add_run(desc)

doc.add_page_break()

# ==================== 11. PROTOTYPE LIMITATIONS ====================
doc.add_heading('11. Prototype Limitations', level=1)

doc.add_paragraph('As a prototype, this system has the following limitations:')
limitations = [
    'Not production-hardened: Additional security measures needed for live deployment',
    'Limited scalability testing: Performance under high load not validated',
    'Email notifications: Placeholder implementation, requires SMTP configuration',
    'PDF reports: Basic layout, advanced formatting may be limited',
    'Mobile optimisation: Primarily designed for desktop use',
    'Offline capability: Requires active internet connection',
    'Data migration: No automated migration from existing systems',
    'Multi-language: English only interface',
    'Backup/Recovery: Manual database backup procedures',
    'Rate limiting: Not implemented in prototype',
]
for item in limitations:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ==================== 12. INSTALLATION ====================
doc.add_heading('12. Installation and Setup', level=1)

doc.add_heading('12.1 Prerequisites', level=2)
prereqs = [
    'Python 3.10 or higher',
    'Node.js 18 or higher',
    'PostgreSQL 13+ (or SQLite for development)',
    'Git for version control',
]
for pr in prereqs:
    doc.add_paragraph(pr, style='List Bullet')

doc.add_heading('12.2 Backend Setup', level=2)
backend_steps = [
    '1. Navigate to the BACK directory',
    '2. Create a Python virtual environment: python -m venv venv',
    '3. Activate the virtual environment',
    '4. Install dependencies: pip install -r requirements.txt',
    '5. Copy .env.example to .env and configure database URL and secret key',
    '6. Run database migrations (when implemented): alembic upgrade head',
    '7. Start the server: uvicorn main:app --reload',
    '8. Access API documentation at http://localhost:8000/docs',
]
for s in backend_steps:
    doc.add_paragraph(s, style='List Bullet')

doc.add_heading('12.3 Frontend Setup', level=2)
frontend_steps = [
    '1. Navigate to the FRONT directory',
    '2. Install dependencies: npm install',
    '3. Configure API base URL in environment file if needed',
    '4. Start development server: npm run dev',
    '5. Access the application at http://localhost:5173',
]
for s in frontend_steps:
    doc.add_paragraph(s, style='List Bullet')

doc.add_heading('12.4 Docker Deployment', level=2)
doc.add_paragraph('For containerised deployment:')
docker_steps = [
    '1. Ensure Docker and Docker Compose are installed',
    '2. Run: docker-compose up -d',
    '3. Access API at http://localhost:8000',
    '4. Access frontend at http://localhost:5173',
]
for s in docker_steps:
    doc.add_paragraph(s, style='List Bullet')

doc.add_page_break()

# ==================== 13. FUTURE ENHANCEMENTS ====================
doc.add_heading('13. Future Enhancements', level=1)

doc.add_paragraph('Potential improvements for future versions:')
enhancements = [
    'Email and SMS notifications for critical alerts',
    'Mobile application (React Native or Flutter)',
    'Advanced analytics with machine learning for risk prediction',
    'Integration with external data sources (financial systems, HR systems)',
    'Multi-tenancy for managing multiple institutions',
    'Advanced reporting with customisable templates',
    'Real-time collaboration features',
    'API rate limiting and throttling',
    'Comprehensive automated testing suite',
    'Internationalisation (i18n) support',
    'Single sign-on (SSO) integration',
    'Advanced data visualisation dashboards',
]
for item in enhancements:
    doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ==================== 14. CONCLUSION ====================
doc.add_heading('14. Conclusion', level=1)

doc.add_paragraph(
    'This prototype demonstrates a viable approach to enterprise risk management for Zimbabwean universities. '
    'By combining a robust FastAPI backend with a modern React frontend, the system provides a comprehensive '
    'platform for risk identification, assessment, mitigation tracking, and compliance reporting.'
)
doc.add_paragraph()
doc.add_paragraph(
    'The modular architecture ensures that the system can be extended and customised to meet specific institutional '
    'requirements. The emphasis on security, audit trails, and role-based access control addresses the governance '
    'needs of academic institutions.'
)
doc.add_paragraph()
doc.add_paragraph(
    'While this prototype serves as a proof of concept, the foundation laid here can be built upon to create a '
    'production-ready system that transforms how universities approach enterprise risk management.'
)

doc.add_paragraph()
doc.add_paragraph()
end_para = doc.add_paragraph('--- End of Document ---')
end_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Save document
output_path = r'C:\Users\Administrator\Desktop\DUMI PROTOTYPE.docx'
doc.save(output_path)
print(f'Document saved successfully to: {output_path}')
