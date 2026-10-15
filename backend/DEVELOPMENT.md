# ERM Platform - Development Guide

## Quick Start

### 1. Initial Setup (First Time Only)

```bash
# Clone/navigate to project
cd erm_backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize project structure (creates directories)
python init_project.py

# Create .env from template
cp .env.example .env

# Validate setup
python validate_setup.py
```

### 2. Start Development Server

```bash
# With auto-reload enabled
uvicorn main:app --reload

# Or for production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 3. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Architecture

### Directory Organization

```
erm_backend/
├── main.py              # FastAPI app + lifespan
├── config.py            # Configuration (Pydantic BaseSettings)
├── database.py          # SQLAlchemy async setup
├── models_stub.py       # All models in one file (stub)
├── models/              # Split into individual files (future)
├── schemas/             # Pydantic request/response models
├── routers/             # FastAPI route handlers
├── services/            # Business logic layer
├── utils/               # Helper functions
├── tests/               # Pytest test suite
└── static/              # Downloadable reports
```

### Request Flow

```
FastAPI Router
    ↓
Service Layer (business logic)
    ↓
Database Layer (SQLAlchemy)
    ↓
PostgreSQL/SQLite
```

Routes should NOT have database logic - use services!

## Configuration

### Environment Variables

All configuration is loaded from `.env` file:

```env
# Database
DB_URL=postgresql+asyncpg://erm_user:password@localhost:5432/erm_db

# For SQLite development (default)
DB_URL=sqlite+aiosqlite:///./erm.db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
PRODUCTION_ORIGIN=https://yourdomain.com

# Debug
DEBUG=True
```

### Database Setup

#### Option 1: SQLite (Default - Development Only)

Already configured. Just ensure `aiosqlite` is installed:
```bash
pip install aiosqlite
```

#### Option 2: PostgreSQL (Recommended)

```bash
# Install PostgreSQL 13+
# Create database and user
createdb -U postgres erm_db
psql -U postgres -d erm_db -c \
  "CREATE USER erm_user WITH PASSWORD 'your_password';"
psql -U postgres -d erm_db -c \
  "GRANT ALL PRIVILEGES ON DATABASE erm_db TO erm_user;"

# Update .env
DB_URL=postgresql+asyncpg://erm_user:your_password@localhost:5432/erm_db
```

#### Option 3: Docker Compose (Easiest)

```bash
docker-compose up -d
# Starts PostgreSQL and API together
```

## Common Development Tasks

### Add a New Risk Endpoint

1. **Create Schema** (`schemas/risk_schemas.py`):
```python
from pydantic import BaseModel

class RiskCreate(BaseModel):
    title: str
    description: str
    risk_category: str
    severity: str
```

2. **Create Router** (`routers/risks.py`):
```python
from fastapi import APIRouter, Depends
from schemas.risk_schemas import RiskCreate

router = APIRouter(prefix="/api/v1/risks", tags=["risks"])

@router.post("/")
async def create_risk(risk: RiskCreate, db = Depends(get_db)):
    return await risk_service.create_risk(db, risk)
```

3. **Create Service** (`services/risk_service.py`):
```python
async def create_risk(db: AsyncSession, risk_data: RiskCreate):
    # Business logic here
    new_risk = Risk(**risk_data.dict())
    db.add(new_risk)
    await db.commit()
    return new_risk
```

4. **Include Router** in `main.py`:
```python
from routers import risks
app.include_router(risks.router)
```

5. **Add Tests** (`tests/test_risks.py`):
```python
@pytest.mark.asyncio
async def test_create_risk():
    # Test logic
```

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_risks.py

# Specific test
pytest tests/test_risks.py::test_create_risk

# With coverage
pytest --cov=. --cov-report=html

# Verbose output
pytest -v

# Only failed tests
pytest --lf

# Stop on first failure
pytest -x
```

### Database Migrations

#### Initialize Alembic (One Time)

```bash
alembic init alembic
```

#### Update `alembic/env.py`:

```python
from database import Base
from config import settings

target_metadata = Base.metadata
sqlalchemy_url = settings.db_url
```

#### Create Migration

```bash
# Automatic migration from models
alembic revision --autogenerate -m "Add user table"

# Manual migration
alembic revision -m "Custom migration"
```

#### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# Go to specific revision
alembic upgrade ae1027a6acf
```

### Code Quality

#### Format Code

```bash
pip install black
black .
```

#### Lint Code

```bash
pip install flake8
flake8 .
```

#### Type Check

```bash
pip install mypy
mypy .
```

#### All at once

```bash
black . && flake8 . && mypy . && pytest
```

## Working with Models

### Current Structure

All models are currently in `models_stub.py`. When ready to scale:

1. **Create individual files** in `models/`:
   - `models/user.py`
   - `models/risk.py`
   - etc.

2. **Update imports** in `models/__init__.py`:
```python
from models.user import User, UserRole
from models.risk import Risk, RiskSeverity, RiskStatus
# ... etc
```

3. **Update `database.py`** metadata import:
```python
from models import Base
```

### Model Best Practices

- Use indexes on frequently queried columns
- Add foreign key constraints
- Use enums for fixed values
- Include created_at and updated_at timestamps
- Add `__repr__` for debugging

Example:
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

## Working with Services

Services contain business logic and database operations.

**RULE**: Never put database code in routers!

### Service Structure

```python
# services/user_service.py

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create new user with hashed password."""
    hashed_pwd = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> User:
    """Get user by email."""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()
```

## Working with Schemas

Use Pydantic v2 for request/response validation.

```python
# schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)  # ORM mode
```

## Async/Await Guidelines

### Database Queries

```python
# ✅ CORRECT - Use async queries
from sqlalchemy import select

async def get_risks(db: AsyncSession):
    query = select(Risk).where(Risk.status == "active")
    result = await db.execute(query)
    return result.scalars().all()

# ❌ WRONG - Don't use .all() directly
risks = db.query(Risk).all()  # This won't work!
```

### Dependencies

```python
# ✅ CORRECT - Async dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Verify token
    return user

# Router using dependency
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

## Error Handling

```python
from fastapi import HTTPException

@router.get("/risks/{risk_id}")
async def get_risk(risk_id: int, db = Depends(get_db)):
    risk = await risk_service.get_risk(db, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Creating risk: {risk_data}")
logger.warning("Database slow query detected")
logger.error(f"Failed to create user: {str(e)}")
logger.debug(f"Query result: {result}")
```

## Performance Tips

1. **Use indexes** on frequently filtered columns
2. **Batch operations** when possible
3. **Use connection pooling** (built-in with SQLAlchemy)
4. **Avoid N+1 queries** - use relationships or eager loading
5. **Cache** static data with APScheduler
6. **Monitor** slow queries in development

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set `PRODUCTION_ORIGIN` for CORS
- [ ] Run database migrations
- [ ] Set up SSL/TLS
- [ ] Enable request logging
- [ ] Set up monitoring/alerting
- [ ] Configure automated backups
- [ ] Run security audit

### Docker Deployment

```bash
# Build image
docker build -t erm-api .

# Run with PostgreSQL
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop containers
docker-compose down
```

## Troubleshooting

### ImportError: No module named 'X'

```bash
pip install -r requirements.txt
```

### Database connection error

- Check `DB_URL` in `.env`
- Verify database server is running
- Check network connectivity
- Review database credentials

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn main:app --port 8001
```

### Tests failing

1. Check `.env` is configured
2. Verify database is accessible
3. Review test output carefully
4. Run `python validate_setup.py`

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/asyncio/
- **Pydantic v2**: https://docs.pydantic.dev/latest/
- **PostgreSQL**: https://www.postgresql.org/docs/

## Getting Help

1. Check error messages carefully
2. Review the README.md
3. Check `.env.example` for configuration
4. Review existing code patterns
5. Check test files for examples

---

**Happy coding!** 🚀
