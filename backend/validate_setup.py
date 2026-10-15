"""
Development setup and validation script for ERM Platform.
Run this after initial setup to verify everything is working.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def check_python_version():
    """Verify Python version is 3.10+."""
    print_header("1. Checking Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.10+ required. Found Python {version.major}.{version.minor}")
        return False


def check_dependencies():
    """Verify all dependencies are installed."""
    print_header("2. Checking Dependencies")
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg",
        "alembic",
        "pydantic",
        "pydantic_settings",
        "python_jose",
        "passlib",
        "apscheduler",
        "reportlab",
        "openpyxl",
        "httpx",
        "pytest",
        "pytest_asyncio",
        "dotenv",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_").replace("python_jose", "jose"))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} (NOT INSTALLED)")
            missing.append(package)
    
    return len(missing) == 0


def check_env_file():
    """Verify .env file exists."""
    print_header("3. Checking Environment Configuration")
    env_path = Path(".env")
    if env_path.exists():
        print_success(".env file found")
        return True
    else:
        print_warning(".env file not found")
        print("  Copy .env.example to .env and configure database settings")
        return False


def check_directory_structure():
    """Verify project directory structure."""
    print_header("4. Checking Directory Structure")
    required_dirs = [
        "models",
        "schemas",
        "routers",
        "services",
        "utils",
        "tests",
        "static",
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print_success(f"{directory}/")
        else:
            print_error(f"{directory}/ (MISSING)")
            all_exist = False
    
    return all_exist


def check_file_structure():
    """Verify important files exist."""
    print_header("5. Checking Required Files")
    required_files = [
        "main.py",
        "config.py",
        "database.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "pytest.ini",
        "models_stub.py",
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.isfile(filename):
            print_success(f"{filename}")
        else:
            print_error(f"{filename} (MISSING)")
            all_exist = False
    
    return all_exist


def test_imports():
    """Test that main modules can be imported."""
    print_header("6. Testing Python Imports")
    try:
        import config
        print_success("config module")
        
        import database
        print_success("database module")
        
        import main
        print_success("main module")
        
        return True
    except ImportError as e:
        print_error(f"Import failed: {str(e)}")
        return False


def run_basic_tests():
    """Run basic pytest tests."""
    print_header("7. Running Basic Tests")
    try:
        result = subprocess.run(
            ["pytest", "test_basic.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print_success("All basic tests passed")
            return True
        else:
            print_warning("Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_warning("Tests timed out")
        return False
    except Exception as e:
        print_warning(f"Could not run tests: {str(e)}")
        return False


def print_next_steps():
    """Print next steps for development."""
    print_header("NEXT STEPS")
    print("""
1. ✅ Configure Database:
   - Update DB_URL in .env with your database credentials
   - For PostgreSQL:
     createdb -U postgres erm_db
     psql -U postgres -d erm_db -c "CREATE USER erm_user WITH PASSWORD 'password';"
   - For SQLite (default): Already configured

2. ✅ Start Development Server:
   uvicorn main:app --reload

3. ✅ Access API:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

4. ✅ Split Models (Optional):
   - Move model definitions from models_stub.py to individual files in models/
   - Import in models/__init__.py

5. ✅ Implement Features:
   - Create schemas in schemas/
   - Create routers in routers/
   - Create services in services/
   - Add tests in tests/

6. ✅ Database Migrations:
   - Initialize Alembic: alembic init alembic
   - Create migration: alembic revision --autogenerate -m "Initial"
   - Apply migrations: alembic upgrade head

7. ✅ Use Docker (Optional):
   docker-compose up -d

For more information, see README.md
    """)


def main():
    """Run all validation checks."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ERM Platform - Development Environment Setup Validation".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        (".env File", check_env_file),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_file_structure),
        ("Python Imports", test_imports),
        ("Basic Tests", run_basic_tests),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            results[name] = False
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("All checks passed! Ready for development.")
        print_next_steps()
        return 0
    else:
        print_warning("Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
