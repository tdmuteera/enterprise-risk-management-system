#!/usr/bin/env python3
"""Setup script to initialize project structure."""

import os
import sys

def setup_project():
    """Create project directory structure."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    directories = [
        "models",
        "schemas", 
        "routers",
        "services",
        "utils",
        "tests",
        "static",
        "alembic",
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_path, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created {directory}/")
    
    print("\nProject structure initialized successfully!")

if __name__ == "__main__":
    setup_project()
