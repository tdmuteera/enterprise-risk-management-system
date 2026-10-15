# ERM Platform - Intelligent Enterprise Risk Management Backend

A production-ready FastAPI backend for comprehensive Enterprise Risk Management (ERM) designed specifically for Zimbabwean universities.

## Features

- 🔐 **Secure Authentication** - JWT-based authentication with role-based access control
- 📊 **Risk Management** - Complete risk register with scoring and assessment
- 🎯 **Mitigation Tracking** - Monitor and manage risk mitigation strategies
- 🚨 **Alert System** - Automated alerts for risk escalations and milestones
- 📈 **Reporting** - Generate PDF and Excel reports for compliance
- 🔄 **Audit Trail** - Complete forensic history of all changes
- 🌐 **REST API** - Clean, well-documented OpenAPI/Swagger interface
- 📱 **CORS Enabled** - Seamless integration with React frontend

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn with standard extras
- **Database**: PostgreSQL with SQLAlchemy 2.x async ORM
- **Driver**: asyncpg for high-performance async database access
- **Authentication**: Python-jose with cryptography
- **Password Hashing**: Passlib with bcrypt
- **Scheduling**: APScheduler for background tasks
- **Reports**: ReportLab (PDF) and openpyxl (Excel)
- **Testing**: Pytest with pytest-asyncio
- **Migrations**: Alembic for database versioning

## Project Structure

```
erm_backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration management (Pydantic BaseSettings)
├── database.py                # SQLAlchemy async setup
├── models_stub.py             # ORM models (stub with all models defined)
├── models/                    # To be split into individual model files
│   ├── user.py
│   ├── department.py
│   ├── risk.py
│   ├── risk_link.py
│   ├── risk_history.py
│   ├── mitigation.py
│   └── alert.py
├── schemas/                   # Pydantic v2 request/response schemas
│   ├── user_schemas.py
│   ├── risk_schemas.py
│   ├── department_schemas.py
│   ├── mitigation_schemas.py
│   ├── alert_schemas.py
│   └── common_schemas.py
├── routers/                   # FastAPI APIRouters (one per domain)
│   ├── users.py              # User management & auth
│   ├── risks.py              # Risk CRUD operations
│   ├── departments.py        # Department management
│   ├── mitigations.py        # Mitigation tracking
│   ├── alerts.py             # Alert management
│   └── reports.py            # Report generation
├── services/                  # Business logic (no DB calls in routers)
│   ├── user_service.py       # User management logic
│   ├── risk_service.py       # Risk scoring and analysis
│   ├── department_service.py # Department operations
│   ├── mitigation_service.py # Mitigation strategy logic
│   ├── alert_service.py      # Alert generation
│   └── report_service.py     # Report generation
├── utils/                     # Helper utilities
│   ├── risk_scorer.py        # Risk scoring algorithms
│   ├── forensic_engine.py    # Audit trail & forensics
│   ├── validators.py         # Data validation
│   ├── date_utils.py         # Date/time helpers
│   └── email_service.py      # Email notifications
├── alembic/                   # Database migrations
├── tests/                     # Pytest test suite
│   ├── test_auth.py
│   ├── test_risks.py
│   ├── test_departments.py
│   └── test_integration.py
├── static/                    # Static files & reports
├── requirements.txt           # Python dependencies (pinned versions)
├── .env.example              # Environment variables template
├── README.md                 # This file
└── init_project.py           # Project initialization script
```

## Installation & Setup

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 13+
- pip and virtualenv

### 2. Clone and Setup Environment

```bash
# Navigate to project directory
cd erm_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your database credentials
# Example PostgreSQL setup:
# DB_URL=postgresql+asyncpg://erm_user:your_password@localhost:5432/erm_db
# SECRET_KEY=your-secure-random-secret-key
```

### 5. Database Setup

```bash
# Create PostgreSQL database and user
createdb -U postgres erm_db
psql -U postgres -d erm_db -c "CREATE USER erm_user WITH PASSWORD 'your_password';"
psql -U postgres -d erm_db -c "GRANT ALL PRIVILEGES ON DATABASE erm_db TO erm_user;"

# Or use the SQL commands in .env.example
```

### 6. Initialize Project Structure

```bash
# Create necessary directories and __init__.py files
python init_project.py
```

### 7. Run Database Migrations

```bash
# (To be implemented with Alembic)
# alembic upgrade head
```

### 8. Start Development Server

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with API info
- `GET /health` - Health check (status, DB connection, version)
- `GET /api/v1/info` - API information

### Authentication (To be implemented)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

### Users (To be implemented)
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Risks (To be implemented)
- `GET /api/v1/risks` - List all risks
- `POST /api/v1/risks` - Create new risk
- `GET /api/v1/risks/{id}` - Get risk details
- `PUT /api/v1/risks/{id}` - Update risk
- `DELETE /api/v1/risks/{id}` - Archive risk
- `GET /api/v1/risks/{id}/history` - Risk change history

### Departments (To be implemented)
- `GET /api/v1/departments` - List departments
- `POST /api/v1/departments` - Create department
- `GET /api/v1/departments/{id}` - Get department details
- `PUT /api/v1/departments/{id}` - Update department

### Mitigations (To be implemented)
- `GET /api/v1/mitigations` - List mitigation strategies
- `POST /api/v1/mitigations` - Create mitigation
- `PUT /api/v1/mitigations/{id}` - Update mitigation status

### Alerts (To be implemented)
- `GET /api/v1/alerts` - List alerts
- `PUT /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `PUT /api/v1/alerts/{id}/resolve` - Resolve alert

### Reports (To be implemented)
- `GET /api/v1/reports/risk-register` - Risk register report (PDF/Excel)
- `GET /api/v1/reports/compliance` - Compliance report
- `GET /api/v1/reports/dashboard-data` - Dashboard analytics

## Configuration

Configuration is managed via environment variables in `.env`:

```env
# Database
DB_URL=postgresql+asyncpg://user:password@localhost:5432/erm_db

# Security
SECRET_KEY=your-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
PRODUCTION_ORIGIN=https://erm.yourdomain.com

# Application
DEBUG=False
APP_NAME="ERM Platform"
APP_VERSION="1.0.0"
```

## Development

### Run Tests

```bash
pytest -v
pytest -v --cov=.  # With coverage report
pytest -v -k "test_risk"  # Run specific tests
```

### Database Migrations (Alembic)

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Revert migrations
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Database Schema

The ERM platform manages:

1. **Users** - System users with role-based access control
2. **Departments** - University faculties/departments
3. **Risks** - Risk register with scoring and categorization
4. **Risk Links** - Relationships between related risks
5. **Risk History** - Audit trail of all changes
6. **Mitigations** - Risk mitigation strategies and tracking
7. **Alerts** - System alerts for escalations and milestones

## Security Features

- ✅ Async SQLAlchemy with prepared statements (SQL injection prevention)
- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ Role-based access control (RBAC)
- ✅ CORS protection
- ✅ Environment-based secret management
- ✅ Comprehensive audit trail
- ✅ Database connection pooling

## Performance Considerations

- Async/await for non-blocking I/O
- PostgreSQL connection pooling
- Database indexes on commonly queried fields
- SQLAlchemy query optimization
- Caching strategies (to be implemented)
- Background task scheduling with APScheduler

## Deployment

### Docker

A Dockerfile will be provided for containerized deployment.

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure production database URL
- [ ] Set `PRODUCTION_ORIGIN` for CORS
- [ ] Run database migrations
- [ ] Set up SSL/TLS certificate
- [ ] Configure logging and monitoring
- [ ] Set up automated backups
- [ ] Implement rate limiting
- [ ] Enable request logging

## API Documentation

Once the server is running, full API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

When adding new features:

1. Create models in `models/` (or extend `models_stub.py`)
2. Create request/response schemas in `schemas/`
3. Create business logic in `services/`
4. Create API routers in `routers/`
5. Add tests in `tests/`
6. Update this README with new endpoints

## Support

For issues or questions about the ERM Platform:
- Check the API documentation at `/docs`
- Review the project structure above
- Check the `.env.example` for configuration options

## License

Proprietary - Zimbabwean Universities ERM Project

## Changelog

### Version 1.0.0 (Initial Release)
- Project scaffolding and structure
- Core configuration setup
- Database connection and async support
- Health check endpoint
- Stub models and service structure
