#!/usr/bin/env python3
"""
Database seed script for ERM Platform.
Creates initial departments, users, risks, and relationships.

Usage:
    python db_seed.py

Requires:
    - PostgreSQL running locally
    - .env file configured with DB_URL
    - Alembic migrations already applied
"""

import asyncio
import os
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import models from models_complete.py
import sys
sys.path.insert(0, os.path.dirname(__file__))

from models_complete import (
    Base,
    Department, User, Risk, RiskLink, MitigationAction, Alert,
    UserRole, RiskCategory, RiskStatus, RiskType, RiskLinkType, MitigationStatus,
    AlertType, AlertSeverity, AlertRole,
)
from config import settings
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


async def seed_database():
    """Seed database with initial data."""
    
    # Create async engine
    engine = create_async_engine(settings.db_url, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    
    async with async_session() as session:
        print("🌱 Seeding ERM Platform database...")
        
        # ====================================================================
        # CREATE DEPARTMENTS
        # ====================================================================
        
        print("\n📁 Creating departments...")
        
        departments_data = [
            {
                "name": "Finance",
                "code": "FIN",
                "description": "Financial management and accounting",
                "head_of_dept": "Dr. John Smith",
                "is_active": True,
            },
            {
                "name": "Human Resources",
                "code": "HR",
                "description": "Human resources and staff management",
                "head_of_dept": "Ms. Sarah Johnson",
                "is_active": True,
            },
            {
                "name": "Academic Affairs",
                "code": "ACAD",
                "description": "Academic programs and student affairs",
                "head_of_dept": "Prof. James Wilson",
                "is_active": True,
            },
            {
                "name": "Information Technology",
                "code": "IT",
                "description": "IT infrastructure and systems",
                "head_of_dept": "Mr. David Brown",
                "is_active": True,
            },
            {
                "name": "Student Affairs",
                "code": "SA",
                "description": "Student support, wellness, housing, and campus life services",
                "head_of_dept": "Dr. Emily Ndlovu",
                "is_active": True,
            },
            {
                "name": "School of Engineering",
                "code": "ENG",
                "description": "Engineering education, laboratories, and professional accreditation activities",
                "head_of_dept": "Prof. Michael Adeyemi",
                "is_active": True,
            },
            {
                "name": "School of Allied Health and Sciences",
                "code": "AHS",
                "description": "Allied health training, clinical placements, and health sciences research",
                "head_of_dept": "Prof. Ruth Maseko",
                "is_active": True,
            },
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept = Department(**dept_data)
            session.add(dept)
            departments[dept_data["code"]] = dept
            print(f"  ✓ {dept_data['code']}: {dept_data['name']}")
        
        await session.flush()
        
        # ====================================================================
        # CREATE USERS
        # ====================================================================
        
        print("\n👥 Creating users...")
        
        users_data = [
            # Admins
            {
                "email": "admin@erm.edu",
                "hashed_password": hash_password("AdminPass123!"),
                "full_name": "Administrator",
                "role": UserRole.ADMIN,
                "department_id": None,
                "is_active": True,
            },
            # Risk Officers
            {
                "email": "risk.officer@erm.edu",
                "hashed_password": hash_password("RiskOff123!"),
                "full_name": "Chief Risk Officer",
                "role": UserRole.RISK_OFFICER,
                "department_id": None,
                "is_active": True,
            },
            {
                "email": "risk.officer.fin@erm.edu",
                "hashed_password": hash_password("RiskFin123!"),
                "full_name": "Finance Risk Officer",
                "role": UserRole.RISK_OFFICER,
                "department_id": None,
                "is_active": True,
            },
            {
                "email": "risk.manager@erm.edu",
                "hashed_password": hash_password("RiskMgr123!"),
                "full_name": "Enterprise Risk Manager",
                "role": UserRole.RISK_MANAGER,
                "department_id": None,
                "is_active": True,
            },
            {
                "email": "head.fin@erm.edu",
                "hashed_password": hash_password("HeadFin123!"),
                "full_name": "Head of Finance",
                "role": UserRole.DEPARTMENT_HEAD,
                "department_id": None,
                "is_active": True,
            },
            # Department Users
            {
                "email": "user.fin@erm.edu",
                "hashed_password": hash_password("FinUser123!"),
                "full_name": "Finance Manager",
                "role": UserRole.DEPT_USER,
                "department_id": None,  # Will set to FIN
                "is_active": True,
            },
            {
                "email": "user.hr@erm.edu",
                "hashed_password": hash_password("HRUser123!"),
                "full_name": "HR Manager",
                "role": UserRole.DEPT_USER,
                "department_id": None,  # Will set to HR
                "is_active": True,
            },
            {
                "email": "user.acad@erm.edu",
                "hashed_password": hash_password("AcadUser123!"),
                "full_name": "Academic Manager",
                "role": UserRole.DEPT_USER,
                "department_id": None,  # Will set to ACAD
                "is_active": True,
            },
            # Executives
            {
                "email": "executive@erm.edu",
                "hashed_password": hash_password("ExecPass123!"),
                "full_name": "University Executive",
                "role": UserRole.EXECUTIVE,
                "department_id": None,
                "is_active": True,
            },
        ]
        
        users = {}
        dept_mappings = {
            "user.fin@erm.edu": departments["FIN"].id,
            "user.hr@erm.edu": departments["HR"].id,
            "user.acad@erm.edu": departments["ACAD"].id,
            "head.fin@erm.edu": departments["FIN"].id,
        }
        
        for user_data in users_data:
            if user_data["email"] in dept_mappings:
                user_data["department_id"] = dept_mappings[user_data["email"]]
            
            user = User(**user_data)
            session.add(user)
            users[user_data["email"]] = user
            print(f"  ✓ {user_data['email']} ({user_data['role'].value})")
        
        await session.flush()
        
        # ====================================================================
        # CREATE RISKS
        # ====================================================================
        
        print("\n⚠️  Creating risks...")
        
        risks_data = [
            # Finance Department Risks
            {
                "title": "Budget Overrun Risk",
                "description": "Risk of exceeding allocated budget in procurement",
                "category": RiskCategory.FINANCIAL,
                "department_id": departments["FIN"].id,
                "owner_id": users["risk.officer.fin@erm.edu"].id,
                "likelihood": 3,
                "impact": 4,
                "velocity": 2,
                "detectability": 2,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            {
                "title": "Irregular Expenditure",
                "description": "Unauthorized or non-compliant financial transactions",
                "category": RiskCategory.COMPLIANCE,
                "department_id": departments["FIN"].id,
                "owner_id": users["user.fin@erm.edu"].id,
                "likelihood": 2,
                "impact": 5,
                "velocity": 3,
                "detectability": 3,
                "status": RiskStatus.IN_PROGRESS,
                "risk_type": RiskType.INHERENT,
            },
            # HR Department Risks
            {
                "title": "Staff Attrition",
                "description": "High turnover of experienced academic staff",
                "category": RiskCategory.HR,
                "department_id": departments["HR"].id,
                "owner_id": users["user.hr@erm.edu"].id,
                "likelihood": 4,
                "impact": 3,
                "velocity": 2,
                "detectability": 1,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            {
                "title": "Payroll System Failure",
                "description": "Breakdown of payroll processing system",
                "category": RiskCategory.IT,
                "department_id": departments["HR"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 1,
                "impact": 5,
                "velocity": 5,
                "detectability": 2,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            # Academic Department Risks
            {
                "title": "Accreditation Non-Compliance",
                "description": "Failure to meet accreditation standards",
                "category": RiskCategory.ACADEMIC,
                "department_id": departments["ACAD"].id,
                "owner_id": users["user.acad@erm.edu"].id,
                "likelihood": 2,
                "impact": 5,
                "velocity": 1,
                "detectability": 2,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            {
                "title": "Student Data Breach",
                "description": "Unauthorized access to student records",
                "category": RiskCategory.IT,
                "department_id": departments["ACAD"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 3,
                "impact": 4,
                "velocity": 4,
                "detectability": 3,
                "status": RiskStatus.ESCALATED,
                "risk_type": RiskType.INHERENT,
            },
            # IT Department Risks
            {
                "title": "Cyber Security Threat",
                "description": "Vulnerability to ransomware and cyberattacks",
                "category": RiskCategory.IT,
                "department_id": departments["IT"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 4,
                "impact": 5,
                "velocity": 4,
                "detectability": 4,
                "status": RiskStatus.IN_PROGRESS,
                "risk_type": RiskType.INHERENT,
            },
            {
                "title": "System Downtime",
                "description": "Critical infrastructure failure",
                "category": RiskCategory.OPERATIONAL,
                "department_id": departments["IT"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 2,
                "impact": 4,
                "velocity": 5,
                "detectability": 1,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            # Student Affairs Risks
            {
                "title": "Student Mental Health Service Overload",
                "description": "Demand for counselling and wellness support exceeds available capacity",
                "category": RiskCategory.OPERATIONAL,
                "department_id": departments["SA"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 4,
                "impact": 4,
                "velocity": 3,
                "detectability": 2,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            # School of Engineering Risks
            {
                "title": "Engineering Lab Safety Non-Compliance",
                "description": "Incomplete adherence to laboratory safety controls and PPE enforcement",
                "category": RiskCategory.COMPLIANCE,
                "department_id": departments["ENG"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 3,
                "impact": 5,
                "velocity": 3,
                "detectability": 3,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            # School of Allied Health and Sciences Risks
            {
                "title": "Clinical Placement Capacity Constraints",
                "description": "Insufficient hospital/clinic placement slots for allied health students",
                "category": RiskCategory.ACADEMIC,
                "department_id": departments["AHS"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 4,
                "impact": 4,
                "velocity": 2,
                "detectability": 2,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            # Reputational Risks
            {
                "title": "Reputational Damage",
                "description": "Negative media coverage affecting institution",
                "category": RiskCategory.REPUTATIONAL,
                "department_id": departments["ACAD"].id,
                "owner_id": users["executive@erm.edu"].id,
                "likelihood": 2,
                "impact": 4,
                "velocity": 3,
                "detectability": 4,
                "status": RiskStatus.OPEN,
                "risk_type": RiskType.INHERENT,
            },
            {
                "title": "Governance Violation",
                "description": "Non-compliance with governance framework",
                "category": RiskCategory.COMPLIANCE,
                "department_id": departments["FIN"].id,
                "owner_id": users["risk.officer.fin@erm.edu"].id,
                "likelihood": 1,
                "impact": 5,
                "velocity": 2,
                "detectability": 4,
                "status": RiskStatus.MITIGATED,
                "risk_type": RiskType.INHERENT,
            },
            # NEW: Risk with Pending Approval status
            {
                "title": "Research Fund Misallocation",
                "description": "Potential misuse of research grant funds across departments",
                "category": RiskCategory.FINANCIAL,
                "department_id": departments["ACAD"].id,
                "owner_id": users["user.acad@erm.edu"].id,
                "likelihood": 2,
                "impact": 4,
                "velocity": 2,
                "detectability": 3,
                "status": RiskStatus.PENDING_APPROVAL,
                "risk_type": RiskType.INHERENT,
            },
            # NEW: Risk with Approved status
            {
                "title": "Vendor Lock-in Risk",
                "description": "Over-dependence on single IT vendor for critical systems",
                "category": RiskCategory.IT,
                "department_id": departments["IT"].id,
                "owner_id": users["risk.officer@erm.edu"].id,
                "likelihood": 3,
                "impact": 3,
                "velocity": 1,
                "detectability": 2,
                "status": RiskStatus.APPROVED,
                "risk_type": RiskType.INHERENT,
                "reviewer_id": None,  # Will be set after flush
                "review_justification": "Risk properly documented with adequate controls proposed",
                "reviewed_at": datetime.now(),
            },
        ]
        
        risks = {}
        for idx, risk_data in enumerate(risks_data):
            # Compute risk score
            score = (
                risk_data["likelihood"] *
                risk_data["impact"] *
                risk_data["velocity"] *
                risk_data["detectability"]
            )
            risk_data["risk_score"] = float(score)
            
            # Set reviewer_id for the approved risk
            if risk_data.get("reviewer_id") is None and risk_data.get("review_justification"):
                risk_data["reviewer_id"] = users["risk.officer@erm.edu"].id
            
            risk = Risk(**risk_data)
            session.add(risk)
            risks[idx] = risk
            print(
                f"  ✓ {risk_data['title']} "
                f"(score: {score}, category: {risk_data['category'].value})"
            )
        
        await session.flush()
        
        # Create a Residual Risk linked to an inherent risk via parent_risk_id
        print("\n  Adding residual risk linked to Budget Overrun Risk...")
        residual_risk = Risk(
            title="Budget Overrun Risk (Residual)",
            description="Residual risk after implementing budget approval controls",
            category=RiskCategory.FINANCIAL,
            department_id=departments["FIN"].id,
            owner_id=users["risk.officer.fin@erm.edu"].id,
            likelihood=2,
            impact=3,
            velocity=2,
            detectability=1,
            risk_score=float(2 * 3 * 2 * 1),
            status=RiskStatus.OPEN,
            risk_type=RiskType.RESIDUAL,
            parent_risk_id=risks[0].id,
        )
        session.add(residual_risk)
        risks[len(risks_data)] = residual_risk
        print(f"  ✓ Budget Overrun Risk (Residual) (score: 12, parent: {risks[0].title})")
        
        await session.flush()
        
        # ====================================================================
        # CREATE RISK LINKS (Cross-Department Dependencies)
        # ====================================================================
        
        print("\n🔗 Creating risk links...")
        
        risk_links_data = [
            {
                "source_risk_id": risks[1].id,  # Irregular Expenditure
                "target_risk_id": risks[9].id,  # Governance Violation
                "link_type": RiskLinkType.CAUSES,
                "weight": 0.9,
                "notes": "Irregular expenditure can lead to governance violations",
                "created_by_id": users["risk.officer@erm.edu"].id,
            },
            {
                "source_risk_id": risks[4].id,  # Student Data Breach
                "target_risk_id": risks[6].id,  # Cyber Security Threat
                "link_type": RiskLinkType.RELATED_TO,
                "weight": 0.8,
                "notes": "Both related to cybersecurity infrastructure",
                "created_by_id": users["risk.officer@erm.edu"].id,
            },
            {
                "source_risk_id": risks[4].id,  # Student Data Breach
                "target_risk_id": risks[8].id,  # Reputational Damage
                "link_type": RiskLinkType.ESCALATES,
                "weight": 0.95,
                "notes": "Data breach escalates to reputational risk",
                "created_by_id": users["risk.officer@erm.edu"].id,
            },
        ]
        
        for link_data in risk_links_data:
            link = RiskLink(**link_data)
            session.add(link)
            print(f"  ✓ Link created (weight: {link_data['weight']})")
        
        await session.flush()
        
        # ====================================================================
        # CREATE MITIGATION ACTIONS
        # ====================================================================
        
        print("\n🛡️  Creating mitigation actions...")
        
        mitigations_data = [
            {
                "risk_id": risks[0].id,  # Budget Overrun
                "description": "Implement strict budget approval process",
                "assigned_to_id": users["user.fin@erm.edu"].id,
                "due_date": datetime.now() + timedelta(days=30),
                "status": MitigationStatus.IN_PROGRESS,
            },
            {
                "risk_id": risks[4].id,  # Student Data Breach
                "description": "Upgrade encryption protocols",
                "assigned_to_id": users["risk.officer@erm.edu"].id,
                "due_date": datetime.now() + timedelta(days=14),
                "status": MitigationStatus.PENDING,
            },
            {
                "risk_id": risks[6].id,  # Cyber Security Threat
                "description": "Implement EDR and threat detection",
                "assigned_to_id": users["risk.officer@erm.edu"].id,
                "due_date": datetime.now() + timedelta(days=45),
                "status": MitigationStatus.IN_PROGRESS,
            },
        ]
        
        for mit_data in mitigations_data:
            mitigation = MitigationAction(**mit_data)
            session.add(mitigation)
            print(f"  ✓ {mit_data['description']}")
        
        await session.flush()
        
        # ====================================================================
        # CREATE ALERTS
        # ====================================================================
        
        print("\n🚨 Creating alerts...")
        
        alerts_data = [
            {
                "alert_type": AlertType.HIGH_RISK,
                "risk_id": risks[4].id,  # Student Data Breach
                "message": "Critical: Student data breach detected with immediate attention required",
                "severity": AlertSeverity.CRITICAL,
                "is_read": False,
                "is_dismissed": False,
                "created_for_role": AlertRole.EXECUTIVE,
            },
            {
                "alert_type": AlertType.OVERDUE_MITIGATION,
                "risk_id": risks[0].id,  # Budget Overrun
                "message": "Warning: Mitigation action for budget risk is approaching deadline",
                "severity": AlertSeverity.WARNING,
                "is_read": False,
                "is_dismissed": False,
                "created_for_role": AlertRole.RISK_OFFICER,
            },
            {
                "alert_type": AlertType.RISK_CHAIN_DETECTED,
                "risk_id": risks[1].id,  # Irregular Expenditure
                "message": "Risk chain detected: Irregular expenditure may trigger governance violations",
                "severity": AlertSeverity.WARNING,
                "is_read": False,
                "is_dismissed": False,
                "created_for_role": AlertRole.ALL,
            },
            {
                "alert_type": AlertType.EMERGING_INSTITUTIONAL,
                "risk_id": None,
                "message": "Emerging risk: Reputational damage from recent incidents",
                "severity": AlertSeverity.WARNING,
                "is_read": False,
                "is_dismissed": False,
                "created_for_role": AlertRole.EXECUTIVE,
            },
        ]
        
        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            session.add(alert)
            print(f"  ✓ {alert_data['alert_type'].value}: {alert_data['severity'].value}")
        
        # ====================================================================
        # COMMIT ALL
        # ====================================================================
        
        await session.commit()
        print("\n✅ Database seeding completed successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("SEED DATA SUMMARY")
        print("="*60)
        print(f"Departments:      {len(departments)}")
        print(f"Users:            {len(users)}")
        print(f"Risks:            {len(risks)} (incl. 1 residual, 1 pending approval, 1 approved)")
        print(f"Risk Links:       {len(risk_links_data)}")
        print(f"Mitigations:      {len(mitigations_data)}")
        print(f"Alerts:           {len(alerts_data)}")
        print("="*60 + "\n")


async def main():
    """Main entry point."""
    try:
        await seed_database()
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
