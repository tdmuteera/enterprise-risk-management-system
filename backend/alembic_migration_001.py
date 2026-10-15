"""
Initial ERM Platform schema migration.

This migration creates all tables for the ERM Platform:
- departments
- users
- risks
- risk_links
- risk_history
- mitigation_actions
- alerts

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-04-21

Usage:
    1. Replace this file in alembic/versions/ after initializing Alembic
    2. Run: alembic upgrade head
    3. Then seed data: python db_seed.py
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""
    
    # Create ENUM types (PostgreSQL specific)
    user_role_enum = postgresql.ENUM(
        'admin', 'risk_officer', 'dept_user', 'executive',
        name='user_role'
    )
    user_role_enum.create(op.get_bind())
    
    risk_category_enum = postgresql.ENUM(
        'Financial', 'HR', 'Academic', 'IT', 'Compliance', 'Operational', 'Reputational',
        name='risk_category'
    )
    risk_category_enum.create(op.get_bind())
    
    risk_status_enum = postgresql.ENUM(
        'Open', 'In-Progress', 'Mitigated', 'Closed', 'Escalated',
        name='risk_status'
    )
    risk_status_enum.create(op.get_bind())
    
    risk_link_type_enum = postgresql.ENUM(
        'causes', 'related_to', 'escalates', 'triggers',
        name='risk_link_type'
    )
    risk_link_type_enum.create(op.get_bind())
    
    risk_history_action_enum = postgresql.ENUM(
        'created', 'updated', 'status_changed', 'score_changed', 'deleted',
        name='risk_history_action'
    )
    risk_history_action_enum.create(op.get_bind())
    
    mitigation_status_enum = postgresql.ENUM(
        'Pending', 'In-Progress', 'Overdue', 'Completed',
        name='mitigation_status'
    )
    mitigation_status_enum.create(op.get_bind())
    
    alert_type_enum = postgresql.ENUM(
        'HighRisk', 'ForensicFlag', 'OverdueMitigation', 'EmergingInstitutional',
        'RiskSuppression', 'RiskChainDetected',
        name='alert_type'
    )
    alert_type_enum.create(op.get_bind())
    
    alert_severity_enum = postgresql.ENUM(
        'Info', 'Warning', 'Critical',
        name='alert_severity'
    )
    alert_severity_enum.create(op.get_bind())
    
    alert_role_enum = postgresql.ENUM(
        'all', 'executive', 'risk_officer',
        name='alert_role'
    )
    alert_role_enum.create(op.get_bind())
    
    # ========================================================================
    # Create departments table
    # ========================================================================
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(4), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('head_of_dept', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_departments_id', 'departments', ['id'])
    op.create_index('ix_departments_name', 'departments', ['name'])
    op.create_index('ix_departments_code', 'departments', ['code'])
    op.create_index('ix_departments_is_active', 'departments', ['is_active'])
    
    # ========================================================================
    # Create users table
    # ========================================================================
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', user_role_enum, server_default='dept_user', nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_department_id', 'users', ['department_id'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    
    # ========================================================================
    # Create risks table
    # ========================================================================
    op.create_table(
        'risks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', risk_category_enum, nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('likelihood', sa.Integer(), nullable=False),
        sa.Column('impact', sa.Integer(), nullable=False),
        sa.Column('velocity', sa.Integer(), nullable=False),
        sa.Column('detectability', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('status', risk_status_enum, server_default='Open', nullable=False),
        sa.Column('institutional_risk_index', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('likelihood BETWEEN 1 AND 5', name='ck_risk_likelihood'),
        sa.CheckConstraint('impact BETWEEN 1 AND 5', name='ck_risk_impact'),
        sa.CheckConstraint('velocity BETWEEN 1 AND 5', name='ck_risk_velocity'),
        sa.CheckConstraint('detectability BETWEEN 1 AND 5', name='ck_risk_detectability'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_risks_id', 'risks', ['id'])
    op.create_index('ix_risks_title', 'risks', ['title'])
    op.create_index('ix_risks_category', 'risks', ['category'])
    op.create_index('ix_risks_department_id', 'risks', ['department_id'])
    op.create_index('ix_risks_owner_id', 'risks', ['owner_id'])
    op.create_index('ix_risks_status', 'risks', ['status'])
    op.create_index('idx_risk_dept_status', 'risks', ['department_id', 'status'])
    op.create_index('idx_risk_score_desc', 'risks', ['risk_score'])
    
    # ========================================================================
    # Create risk_links table
    # ========================================================================
    op.create_table(
        'risk_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('source_risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('link_type', risk_link_type_enum, nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_risk_id'], ['risks.id'], ),
        sa.ForeignKeyConstraint(['target_risk_id'], ['risks.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_risk_links_id', 'risk_links', ['id'])
    op.create_index('ix_risk_links_source_risk_id', 'risk_links', ['source_risk_id'])
    op.create_index('ix_risk_links_target_risk_id', 'risk_links', ['target_risk_id'])
    op.create_index('ix_risk_links_created_by_id', 'risk_links', ['created_by_id'])
    
    # ========================================================================
    # Create risk_history table (immutable audit log)
    # ========================================================================
    op.create_table(
        'risk_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', risk_history_action_enum, nullable=False),
        sa.Column('changed_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('previous_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['risk_id'], ['risks.id'], ),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_risk_history_id', 'risk_history', ['id'])
    op.create_index('ix_risk_history_risk_id', 'risk_history', ['risk_id'])
    op.create_index('ix_risk_history_changed_by_id', 'risk_history', ['changed_by_id'])
    op.create_index('ix_risk_history_changed_at', 'risk_history', ['changed_at'])
    op.create_index('idx_risk_history_changed_at_desc', 'risk_history', ['changed_at'])
    
    # ========================================================================
    # Create mitigation_actions table
    # ========================================================================
    op.create_table(
        'mitigation_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', mitigation_status_enum, server_default='Pending', nullable=False),
        sa.Column('effectiveness_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['risk_id'], ['risks.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_mitigation_actions_id', 'mitigation_actions', ['id'])
    op.create_index('ix_mitigation_actions_risk_id', 'mitigation_actions', ['risk_id'])
    op.create_index('ix_mitigation_actions_assigned_to_id', 'mitigation_actions', ['assigned_to_id'])
    op.create_index('ix_mitigation_actions_status', 'mitigation_actions', ['status'])
    
    # ========================================================================
    # Create alerts table
    # ========================================================================
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('alert_type', alert_type_enum, nullable=False),
        sa.Column('risk_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', alert_severity_enum, server_default='Info', nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_dismissed', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_for_role', alert_role_enum, server_default='all', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['risk_id'], ['risks.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_alerts_id', 'alerts', ['id'])
    op.create_index('ix_alerts_alert_type', 'alerts', ['alert_type'])
    op.create_index('ix_alerts_risk_id', 'alerts', ['risk_id'])
    op.create_index('ix_alerts_severity', 'alerts', ['severity'])
    op.create_index('ix_alerts_is_read', 'alerts', ['is_read'])
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'])


def downgrade() -> None:
    """Drop all schema objects."""
    
    # Drop tables in reverse order
    op.drop_table('alerts')
    op.drop_table('mitigation_actions')
    op.drop_table('risk_history')
    op.drop_table('risk_links')
    op.drop_table('risks')
    op.drop_table('users')
    op.drop_table('departments')
    
    # Drop ENUM types
    sa.Enum('alert_role', name='alert_role').drop(op.get_bind())
    sa.Enum('alert_severity', name='alert_severity').drop(op.get_bind())
    sa.Enum('alert_type', name='alert_type').drop(op.get_bind())
    sa.Enum('mitigation_status', name='mitigation_status').drop(op.get_bind())
    sa.Enum('risk_history_action', name='risk_history_action').drop(op.get_bind())
    sa.Enum('risk_link_type', name='risk_link_type').drop(op.get_bind())
    sa.Enum('risk_status', name='risk_status').drop(op.get_bind())
    sa.Enum('risk_category', name='risk_category').drop(op.get_bind())
    sa.Enum('user_role', name='user_role').drop(op.get_bind())
