#!/usr/bin/env python3
"""
ERM Platform Backend - Quick Reference & File Index

This file serves as a navigation guide for the project structure.
"""

FILE_INDEX = {
    "🚀 Getting Started": {
        "README.md": "Read this first - project overview and setup instructions",
        "DEVELOPMENT.md": "Complete development guide with examples and patterns",
        "PROJECT_SETUP_COMPLETE.md": "Status and quick start (30 seconds)",
        ".env.example": "Environment variables template - copy to .env",
    },
    
    "🔧 Core Application": {
        "main.py": "FastAPI entry point - app creation, lifespan, endpoints",
        "config.py": "Pydantic BaseSettings - environment configuration",
        "database.py": "SQLAlchemy async setup - engine, sessions, DB checks",
        "models_stub.py": "All ORM models (User, Risk, Department, etc.)",
    },
    
    "📦 Project Structure": {
        "models/": "ORM models directory (to be split from models_stub.py)",
        "schemas/": "Pydantic request/response schemas",
        "routers/": "FastAPI route handlers (APIRouters)",
        "services/": "Business logic layer (no DB calls in routers!)",
        "utils/": "Helper functions (scoring, validation, etc.)",
        "tests/": "Pytest test suite",
        "static/": "Downloaded reports and static files",
        "alembic/": "Database migration files",
    },
    
    "⚙️ Configuration": {
        ".env": "Development environment variables (DO NOT COMMIT!)",
        "pytest.ini": "Pytest configuration",
        "requirements.txt": "Python dependencies (pinned versions)",
        "Dockerfile": "Production container image",
        "docker-compose.yml": "Multi-container setup (API + PostgreSQL)",
    },
    
    "🧪 Testing & Validation": {
        "test_basic.py": "Basic health/endpoint tests",
        "validate_setup.py": "Setup validation script - run this first!",
        "init_project.py": "Project initialization (creates directories)",
    },
    
    "📚 Documentation": {
        "MODELS_README.md": "Guide for organizing ORM models",
        "ROUTERS_README.md": "Guide for creating API routers",
        "SERVICES_README.md": "Guide for business logic services",
        "SCHEMAS_README.md": "Guide for Pydantic schemas",
        "UTILS_README.md": "Guide for utility functions",
        "ALEMBIC_SETUP.md": "Database migration setup instructions",
    },
}

QUICK_COMMANDS = {
    "Setup": [
        "python -m venv venv",
        "venv\\Scripts\\activate  # Windows",
        "source venv/bin/activate  # macOS/Linux",
        "pip install -r requirements.txt",
    ],
    
    "Validate": [
        "python validate_setup.py",
    ],
    
    "Development": [
        "uvicorn main:app --reload",
        "# API: http://localhost:8000",
        "# Docs: http://localhost:8000/docs",
    ],
    
    "Testing": [
        "pytest -v",
        "pytest -v --cov=.",
        "pytest test_basic.py -v",
    ],
    
    "Database": [
        "# PostgreSQL setup:",
        "createdb -U postgres erm_db",
        "psql -U postgres -d erm_db -c \"CREATE USER erm_user WITH PASSWORD 'password';\"",
        "",
        "# Or use Docker:",
        "docker-compose up -d",
    ],
    
    "Docker": [
        "docker build -t erm-api .",
        "docker-compose up -d",
        "docker-compose logs -f api",
        "docker-compose down",
    ],
}

KEY_FEATURES = [
    "✅ FastAPI with async/await",
    "✅ SQLAlchemy 2.x with asyncpg",
    "✅ Pydantic v2 for validation",
    "✅ JWT authentication ready",
    "✅ CORS configured",
    "✅ Health check endpoint",
    "✅ Docker support",
    "✅ Comprehensive tests",
    "✅ Full documentation",
    "✅ Environment-based config",
]

NEXT_STEPS = [
    "1. Run: python validate_setup.py",
    "2. Update .env with database credentials",
    "3. Start server: uvicorn main:app --reload",
    "4. Visit: http://localhost:8000/docs",
    "5. Review: DEVELOPMENT.md for patterns",
    "6. Start implementing endpoints!",
]

ENDPOINTS_AVAILABLE = {
    "Health & Info": [
        "GET /",
        "GET /health",
        "GET /api/v1/info",
        "GET /docs (Swagger)",
        "GET /redoc (ReDoc)",
    ],
    
    "To Be Implemented": [
        "POST /api/v1/auth/register",
        "POST /api/v1/auth/login",
        "GET /api/v1/risks",
        "POST /api/v1/risks",
        "GET /api/v1/departments",
        "GET /api/v1/users",
        "# ... and many more!",
    ],
}

MODELS_INCLUDED = [
    "👤 User - System users with roles",
    "🏫 Department - University departments",
    "⚠️  Risk - Risk register with scoring",
    "🔗 RiskLink - Relationships between risks",
    "📋 RiskHistory - Audit trail",
    "🛡️  Mitigation - Risk mitigation strategies",
    "🚨 Alert - System alerts",
]

DATABASE_ENUMS = [
    "UserRole: ADMIN, RISK_OFFICER, DEPARTMENT_HEAD, AUDITOR, VIEWER",
    "RiskSeverity: CRITICAL, HIGH, MEDIUM, LOW",
    "RiskStatus: NEW, ACTIVE, MITIGATING, RESOLVED, ARCHIVED",
    "MitigationStatus: PLANNED, IN_PROGRESS, COMPLETED, ON_HOLD, CANCELLED",
    "AlertType: RISK_ESCALATION, MITIGATION_DUE, POLICY_VIOLATION, AUDIT_ALERT, SYSTEM_ALERT",
    "AlertStatus: PENDING, ACKNOWLEDGED, RESOLVED, DISMISSED",
]


def print_section(title, items):
    """Print formatted section."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    
    if isinstance(items, dict):
        for category, contents in items.items():
            print(f"\n  {category}:")
            for item in contents:
                print(f"    • {item}")
    elif isinstance(items, list):
        for item in items:
            if item.startswith("#") or item == "":
                print(f"    {item}")
            else:
                print(f"    • {item}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  ERM Platform Backend - Quick Reference".center(68) + "║")
    print("║" + "  Intelligent Enterprise Risk Management for Zimbabwean Universities".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Print file index
    print_section("📁 File Index", FILE_INDEX)
    
    # Print quick commands
    print_section("⚡ Quick Commands", QUICK_COMMANDS)
    
    # Print features
    print_section("✨ Key Features", KEY_FEATURES)
    
    # Print models
    print_section("📊 Database Models", MODELS_INCLUDED)
    
    # Print enums
    print_section("📋 Database Enumerations", DATABASE_ENUMS)
    
    # Print endpoints
    print_section("🔌 API Endpoints", ENDPOINTS_AVAILABLE)
    
    # Print next steps
    print_section("🚀 Next Steps", NEXT_STEPS)
    
    print("\n" + "="*70)
    print("  Documentation")
    print("="*70)
    print("""
  • Main README: Start with README.md for setup
  • Development: See DEVELOPMENT.md for patterns and examples
  • API Docs: http://localhost:8000/docs (when server running)
  • Setup Status: Check PROJECT_SETUP_COMPLETE.md
  
  Questions? Review the appropriate _README.md file in root directory.
""")
    
    print("="*70)
    print("  Production Checklist")
    print("="*70)
    print("""
  ☐ Change SECRET_KEY
  ☐ Set DEBUG=False
  ☐ Configure production database
  ☐ Update CORS_ORIGINS for production
  ☐ Set PRODUCTION_ORIGIN
  ☐ Configure logging
  ☐ Set up monitoring
  ☐ Enable backups
  ☐ Run security audit
""")
    
    print("\n🎉 Project is ready for development!")
    print("📖 Start with: python validate_setup.py\n")
