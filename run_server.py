#!/usr/bin/env python
"""
Django Development Server Startup with Virtual Environment
This script ensures the correct Python virtual environment is used for development
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start Django development server with proper venv setup"""
    
    # Get project root
    project_root = Path(__file__).parent
    venv_path = project_root / 'venv_py311' / 'Scripts' / 'python.exe'
    
    # Check venv exists
    if not venv_path.exists():
        print("❌ ERROR: Virtual environment not found at venv_py311")
        print("Please create it: python -m venv venv_py311")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("PNEUMONIA DIAGNOSIS - DJANGO DEVELOPMENT SERVER")
    print("="*70 + "\n")
    
    # Verify Django is installed
    result = subprocess.run(
        [str(venv_path), '-c', 'import django'],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("⚠️  Django not installed. Installing requirements...")
        subprocess.run([str(venv_path), '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Run migrations
    print("Running database migrations...")
    migrate_result = subprocess.run(
        [str(venv_path), 'manage.py', 'migrate', '--noinput'],
        cwd=str(project_root)
    )
    
    if migrate_result.returncode == 0:
        print("✓ Database migrations applied successfully\n")
    else:
        print("⚠️  Warning: Migration check returned errors\n")
    
    # Start server
    print("="*70)
    print("Starting development server on http://127.0.0.1:8000/")
    print("Press CTRL+C to stop")
    print("="*70 + "\n")
    
    # Start Django dev server
    os.chdir(str(project_root))
    subprocess.run(
        [str(venv_path), 'manage.py', 'runserver'],
        cwd=str(project_root)
    )

if __name__ == '__main__':
    main()
