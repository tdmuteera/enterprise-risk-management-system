"""
ERM Platform Database Setup Guide

This guide walks through setting up the complete database schema
with migrations and seed data.
"""

# ============================================================================
# PREREQUISITES
# ============================================================================

"""
Required:
  - PostgreSQL 13+ running locally or remote
  - Python 3.10+ with virtual environment activated
  - Dependencies: pip install -r requirements.txt

Optional:
  - pgAdmin for visual database inspection
  - psql command-line tool
"""

# ============================================================================
# QUICK START (5 minutes)
# ============================================================================

"""
1. Update .env with your PostgreSQL credentials:
   DB_URL=postgresql+asyncpg://erm_user:password@localhost:5432/erm_db

2. Create PostgreSQL database and user (if not using Docker):
   
   psql -U postgres -c "CREATE USER erm_user WITH PASSWORD 'password';"
   psql -U postgres -c "CREATE DATABASE erm_db OWNER erm_user;"
   psql -U postgres -d erm_db -c "GRANT ALL PRIVILEGES ON DATABASE erm_db TO erm_user;"

3. Run migrations:
   
   # Option A: Using Alembic (for production)
   alembic upgrade head
   
   # Option B: Using db_seed.py (includes auto-schema creation)
   python db_seed.py

4. Verify:
   psql -U erm_user -d erm_db -c "SELECT COUNT(*) FROM risks;"
   # Should show: 10 risks

5. Start server:
   uvicorn main:app --reload
   # Access: http://localhost:8000/docs
"""

# ============================================================================
# METHOD 1: DOCKER SETUP (Easiest)
# ============================================================================

"""
1. Start Docker containers:
   docker-compose up -d

2. Wait for PostgreSQL to be ready (~5 seconds):
   docker-compose logs -f postgres

3. In another terminal, seed the database:
   docker-compose exec api python db_seed.py

4. Access database:
   docker-compose exec postgres psql -U erm_user -d erm_db

5. Access API:
   http://localhost:8000/docs
"""

# ============================================================================
# METHOD 2: LOCAL POSTGRESQL SETUP (Manual)
# ============================================================================

"""
1. Install PostgreSQL (if not already installed):
   
   Windows:  https://www.postgresql.org/download/windows/
   macOS:    brew install postgresql
   Linux:    sudo apt-get install postgresql

2. Start PostgreSQL service:
   
   Windows:  Services → Start PostgreSQL
   macOS:    brew services start postgresql
   Linux:    sudo systemctl start postgresql

3. Create database and user:
   
   psql -U postgres
   
   postgres=# CREATE USER erm_user WITH PASSWORD 'your_password';
   postgres=# CREATE DATABASE erm_db OWNER erm_user;
   postgres=# GRANT ALL PRIVILEGES ON DATABASE erm_db TO erm_user;
   postgres=# \\q

4. Configure .env:
   
   DB_URL=postgresql+asyncpg://erm_user:your_password@localhost:5432/erm_db

5. Run migrations:
   
   python db_seed.py
   
   This will:
   - Create all tables
   - Add constraints and indexes
   - Seed initial data
   - Create UUIDs for all records

6. Verify:
   
   psql -U erm_user -d erm_db -c "SELECT * FROM departments;"
   # Should show 4 departments
"""

# ============================================================================
# METHOD 3: ALEMBIC MIGRATIONS (Best Practice)
# ============================================================================

"""
Use this approach for version control and team collaboration.

1. Initialize Alembic (if not done):
   
   alembic init alembic

2. Update alembic/env.py with:
   
   from models_complete import Base
   target_metadata = Base.metadata

3. Place migration file in alembic/versions/:
   
   Copy: alembic_migration_001.py
   To:   alembic/versions/001_initial_schema.py

4. Create initial revision:
   
   alembic revision --autogenerate -m "Initial schema"

5. Apply migration:
   
   alembic upgrade head
   
   This creates all tables, constraints, and indexes.

6. Seed data:
   
   python db_seed.py

7. For future changes:
   
   # Modify models in models_complete.py
   alembic revision --autogenerate -m "Describe change"
   alembic upgrade head
"""

# ============================================================================
# VERIFYING THE SETUP
# ============================================================================

"""
1. Check tables exist:
   psql -U erm_user -d erm_db -c "
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';"
   
   Should show:
   - departments
   - users
   - risks
   - risk_links
   - risk_history
   - mitigation_actions
   - alerts

2. Check data was seeded:
   psql -U erm_user -d erm_db -c "
   SELECT COUNT(*) as dept_count FROM departments;
   SELECT COUNT(*) as user_count FROM users;
   SELECT COUNT(*) as risk_count FROM risks;
   SELECT COUNT(*) as mitigation_count FROM mitigation_actions;
   SELECT COUNT(*) as alert_count FROM alerts;"
   
   Should show:
   - departments: 4
   - users: 7
   - risks: 10
   - mitigation_actions: 3
   - alerts: 4

3. Check constraints:
   psql -U erm_user -d erm_db -c "
   SELECT constraint_name FROM information_schema.table_constraints 
   WHERE table_name='risks' AND constraint_type='CHECK';"
   
   Should show:
   - ck_risk_likelihood
   - ck_risk_impact
   - ck_risk_velocity
   - ck_risk_detectability

4. Check indexes:
   psql -U erm_user -d erm_db -c "
   SELECT indexname FROM pg_indexes WHERE tablename='risks';"
   
   Should include:
   - idx_risk_dept_status
   - idx_risk_score_desc
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Error: "FATAL: Ident authentication failed for user 'erm_user'"

Solution:
  Update PostgreSQL configuration to allow password authentication:
  
  1. Find pg_hba.conf (usually /etc/postgresql/13/main/pg_hba.conf)
  2. Change line: local   all             all                     peer
     To:          local   all             all                     md5
  3. Restart PostgreSQL

Error: "Database does not exist"

Solution:
  createdb -U postgres erm_db
  psql -U postgres -d erm_db -c "
    CREATE USER erm_user WITH PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE erm_db TO erm_user;"

Error: "permission denied for schema public"

Solution:
  psql -U postgres -d erm_db -c "
    GRANT ALL PRIVILEGES ON SCHEMA public TO erm_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO erm_user;"

Error: "asyncpg not installed"

Solution:
  pip install asyncpg

Error: "Alembic command not found"

Solution:
  pip install alembic

Error: Tables not created after running db_seed.py

Solution:
  1. Check .env has correct DB_URL
  2. Verify PostgreSQL is running
  3. Check database user has permissions
  4. Run with verbose output: python db_seed.py (shows errors)
"""

# ============================================================================
# DATABASE INSPECTION
# ============================================================================

"""
View all departments:
  psql -U erm_user -d erm_db -c "SELECT * FROM departments;"

View high-risk risks:
  psql -U erm_user -d erm_db -c "
  SELECT id, title, risk_score, status FROM risks 
  WHERE risk_score > 100 
  ORDER BY risk_score DESC;"

View risk history for specific risk:
  psql -U erm_user -d erm_db -c "
  SELECT * FROM risk_history 
  WHERE risk_id = 'uuid-here' 
  ORDER BY changed_at DESC;"

View users by role:
  psql -U erm_user -d erm_db -c "
  SELECT email, role, full_name FROM users 
  ORDER BY role;"

Export data to CSV:
  psql -U erm_user -d erm_db -c "
  \\COPY (SELECT * FROM risks) TO 'risks.csv' WITH CSV HEADER;"

View table structure:
  psql -U erm_user -d erm_db -c "
  \\d risks"
"""

# ============================================================================
# RESET DATABASE (Development Only)
# ============================================================================

"""
WARNING: This will DELETE all data!

Approach 1: Drop and recreate:
  psql -U postgres -c "DROP DATABASE IF EXISTS erm_db;"
  psql -U postgres -c "CREATE DATABASE erm_db OWNER erm_user;"
  python db_seed.py

Approach 2: Using Alembic downgrade:
  alembic downgrade base
  alembic upgrade head
  python db_seed.py

Approach 3: Clear tables (keep schema):
  psql -U erm_user -d erm_db -c "
  TRUNCATE TABLE alerts CASCADE;
  TRUNCATE TABLE mitigation_actions CASCADE;
  TRUNCATE TABLE risk_history CASCADE;
  TRUNCATE TABLE risk_links CASCADE;
  TRUNCATE TABLE risks CASCADE;
  TRUNCATE TABLE users CASCADE;
  TRUNCATE TABLE departments CASCADE;"
  python db_seed.py
"""

# ============================================================================
# FILES INVOLVED
# ============================================================================

"""
Core Models:
  models_complete.py          - All ORM models with relationships
  models_base.py              - Enumerations (legacy)

Database Setup:
  database.py                 - Async engine and sessions
  config.py                   - Configuration loading

Migrations:
  alembic_migration_001.py    - Full schema migration
  ALEMBIC_SETUP.md            - Migration instructions

Seeding:
  db_seed.py                  - Seed script (runnable standalone)

Documentation:
  DB_SCHEMA_ARCHITECTURE.md   - Complete schema docs
  DATABASE_SETUP.md           - This file

Configuration:
  .env                        - Database credentials
  .env.example                - Template
"""

# ============================================================================
# PRODUCTION CONSIDERATIONS
# ============================================================================

"""
1. Security:
   - Use strong passwords for erm_user
   - Don't store credentials in code
   - Use environment variables
   - Enable SSL/TLS for DB connection
   - Restrict database access by IP

2. Performance:
   - Consider partitioning risk_history table
   - Add materialized views for dashboards
   - Enable full-text search on titles/descriptions
   - Archive old risk history periodically

3. Backup:
   - Daily automated backups
   - Test restore procedures
   - Keep backups offsite
   
   Backup command:
   pg_dump -U erm_user -d erm_db > backup_$(date +%Y%m%d).sql
   
   Restore command:
   psql -U erm_user -d erm_db < backup_20260421.sql

4. Monitoring:
   - Monitor database size growth
   - Watch slow queries
   - Monitor connection pool
   - Set up alerts for failures

5. Maintenance:
   - Analyze tables monthly: ANALYZE;
   - Vacuum regularly: VACUUM ANALYZE;
   - Review and update statistics

6. Scaling:
   - Read replicas for reporting
   - Connection pooling (pgBouncer)
   - Caching layer (Redis) for frequent queries
   - Partition large tables
"""

# ============================================================================
# QUICK REFERENCE COMMANDS
# ============================================================================

"""
Start PostgreSQL:
  docker-compose up -d postgres

Connect to database:
  psql -U erm_user -d erm_db

List tables:
  \\dt

Show table structure:
  \\d risks

List indexes:
  \\di

Run SQL file:
  \\i /path/to/file.sql

Export query to CSV:
  \\COPY (SELECT ...) TO 'file.csv' WITH CSV HEADER;

View database size:
  SELECT pg_size_pretty(pg_database_size('erm_db'));

View table size:
  SELECT pg_size_pretty(pg_total_relation_size('risks'));

Count rows:
  SELECT COUNT(*) FROM risks;

Quit:
  \\q
"""
