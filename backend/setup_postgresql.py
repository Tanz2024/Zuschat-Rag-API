#!/usr/bin/env python3
"""
PostgreSQL Setup and Initialization Script for ZUS Coffee AI Chatbot
"""
import os
import subprocess
import sys
from pathlib import Path

def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f" PostgreSQL is installed: {result.stdout.strip()}")
            return True
        else:
            print(" PostgreSQL is not installed")
            return False
    except FileNotFoundError:
        print(" PostgreSQL is not installed or not in PATH")
        return False

def create_database():
    """Create the zuschat database"""
    try:
        # Try to create the database
        result = subprocess.run(['createdb', 'zuschat'], capture_output=True, text=True)
        if result.returncode == 0:
            print(" Database 'zuschat' created successfully")
        elif "already exists" in result.stderr:
            print(" Database 'zuschat' already exists")
        else:
            print(f" Failed to create database: {result.stderr}")
            return False
        return True
    except FileNotFoundError:
        print(" createdb command not found. Please ensure PostgreSQL is properly installed")
        return False

def setup_environment():
    """Set up environment variables"""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print(" .env file not found")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update DATABASE_URL if needed
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            if 'postgresql://' not in line:
                lines[i] = 'DATABASE_URL=postgresql://postgres:password@localhost:5432/zuschat\n'
                updated = True
            break
    
    if updated:
        with open(env_file, 'w') as f:
            f.writelines(lines)
        print(" Updated .env file with PostgreSQL configuration")
    else:
        print(" .env file already configured for PostgreSQL")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    try:
        print(" Installing Python dependencies...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(" Python dependencies installed successfully")
            return True
        else:
            print(f" Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f" Error installing dependencies: {e}")
        return False

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    try:
        print(" Migrating data from SQLite to PostgreSQL...")
        result = subprocess.run([sys.executable, 'migrate_to_postgresql.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(" Data migration completed successfully")
            print(result.stdout)
            return True
        else:
            print(f" Data migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f" Error during migration: {e}")
        return False

def main():
    """Main setup function"""
    print(" ZUS Coffee AI Chatbot - PostgreSQL Setup")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    steps = [
        ("Checking PostgreSQL installation", check_postgresql_installed),
        ("Creating database", create_database),
        ("Setting up environment", setup_environment),
        ("Installing dependencies", install_dependencies),
        ("Migrating data", migrate_data)
    ]
    
    for step_name, step_func in steps:
        print(f"\n {step_name}...")
        if not step_func():
            print(f"\n Setup failed at step: {step_name}")
            print("Please fix the issue and run the setup again.")
            return False
    
    print("\n PostgreSQL setup completed successfully!")
    print("\nNext steps:")
    print("1. Install spaCy model: python -m spacy download en_core_web_sm")
    print("2. Install Playwright: playwright install")
    print("3. Start the server: uvicorn main:app --reload")
    
    return True

if __name__ == "__main__":
    main()
