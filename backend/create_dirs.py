import os
import sys

def create_structure():
    base = r'c:\Users\Administrator\Desktop\Dissertations\VANA DUMI\BACK'
    
    # Create directories
    dirs = ['models', 'schemas', 'routers', 'services', 'utils', 'tests', 'alembic']
    for d in dirs:
        os.makedirs(os.path.join(base, d), exist_ok=True)
    
    # Create __init__.py files
    init_files = [
        'models/__init__.py',
        'schemas/__init__.py', 
        'routers/__init__.py',
        'services/__init__.py',
        'utils/__init__.py',
        'tests/__init__.py',
    ]
    
    for init_file in init_files:
        path = os.path.join(base, init_file)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('"""Auto-generated module."""\n')
    
    print("Structure created successfully!")

if __name__ == "__main__":
    create_structure()
