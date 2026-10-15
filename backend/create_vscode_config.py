#!/usr/bin/env python3
"""
Create .vscode settings directory and configuration.
"""

import os
import json
from pathlib import Path

def create_vscode_settings():
    """Create .vscode/settings.json configuration."""
    
    base_path = Path(__file__).parent
    vscode_dir = base_path / ".vscode"
    settings_file = vscode_dir / "settings.json"
    
    # Create .vscode directory
    vscode_dir.mkdir(exist_ok=True)
    print(f"✓ Created .vscode/")
    
    # Create settings.json
    settings_content = {
        "python.terminal.useEnvFile": True
    }
    
    with open(settings_file, 'w') as f:
        json.dump(settings_content, f, indent=2)
    
    print(f"✓ Created .vscode/settings.json")
    print(f"✓ Configured: python.terminal.useEnvFile = True")
    print(f"\nVS Code will now automatically use virtual environment!")

if __name__ == "__main__":
    create_vscode_settings()
