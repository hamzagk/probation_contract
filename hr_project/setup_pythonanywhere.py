#!/usr/bin/env python3
"""
PythonAnywhere Setup Script for GIK Institute HR Portal

This script automates the setup process for deploying the HR Portal to PythonAnywhere.
Run this script after cloning your repository to PythonAnywhere.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Helper function to run shell commands with error handling."""
    print(f"\n{description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success!")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("Setting up GIK Institute HR Portal for PythonAnywhere...")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("Error: manage.py not found. Please run this script from your project directory.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("GIK Institute HR Portal - PythonAnywhere Setup")
    print("="*60)
    
    # Step 1: Install dependencies
    success = run_command(
        "pip3 install --user -r requirements_pythonanywhere.txt",
        "Installing required packages..."
    )
    if not success:
        print("Failed to install dependencies. Please check requirements_pythonanywhere.txt")
        return False
    
    # Step 2: Run migrations
    success = run_command(
        "python3 manage.py migrate",
        "Running database migrations..."
    )
    if not success:
        print("Failed to run migrations. This might be OK if first time setup.")
    
    # Step 3: Collect static files
    success = run_command(
        "python3 manage.py collectstatic --noinput",
        "Collecting static files..."
    )
    if not success:
        print("Failed to collect static files.")
        return False
    
    # Step 4: Create superuser if it doesn't exist (optional)
    print("\nCreating superuser (optional)...")
    print("Note: You can skip this step and create a superuser later if needed.")
    create_superuser = input("Do you want to create a superuser now? (y/n): ").lower().strip()
    
    if create_superuser == 'y':
        run_command("python3 manage.py createsuperuser", "Creating superuser...")
    
    print("\n" + "="*60)
    print("Setup completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Go to the 'Web' tab in PythonAnywhere")
    print("2. Click 'Reload' to restart your web application")
    print("3. Your HR Portal should now be accessible via your PythonAnywhere domain")
    print("\nRemember to set your environment variables in the .bashrc file:")
    print("   - SECRET_KEY")
    print("   - DEBUG (False for production)")
    print("   - EMAIL_HOST_USER")
    print("   - EMAIL_HOST_PASSWORD")
    print("   - Other email settings as needed")
    
    return True

if __name__ == "__main__":
    main()