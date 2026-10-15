#!/usr/bin/env python3
"""
Initialize ERM Platform project structure.
Run once before starting the application.
"""

import os
import sys
from pathlib import Path

# Project base directory
PROJECT_ROOT = Path(__file__).parent

def initialize_project():
    """Create all necessary directories and init files."""
    
    print("🔧 Initializing ERM Platform project structure...")
    
    # Directories to create
    directories = [
        "models",
        "schemas",
        "routers",
        "services",
        "utils",
        "tests",
        "alembic",
        "static",
    ]
    
    # Create directories
    for directory in directories:
        dir_path = PROJECT_ROOT / directory
        dir_path.mkdir(exist_ok=True)
        print(f"  ✓ {directory}/")
    
    # Create __init__.py files for Python packages
    init_files = [
        "models/__init__.py",
        "schemas/__init__.py",
        "routers/__init__.py",
        "services/__init__.py",
        "utils/__init__.py",
        "tests/__init__.py",
    ]
    
    init_content = '"""Auto-generated package module."""\n'
    
    for init_file in init_files:
        file_path = PROJECT_ROOT / init_file
        if not file_path.exists():
            file_path.write_text(init_content)
            print(f"  ✓ {init_file}")
    
    print("\n✅ Project structure initialized successfully!")
    print("📝 Next steps:")
    print("   1. Copy .env.example to .env and update database credentials")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Run migrations (once Alembic is configured)")
    print("   4. Start server: uvicorn main:app --reload")

if __name__ == "__main__":
    initialize_project()
