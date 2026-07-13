"""
Post-deployment setup script for HR Portal

This script performs initial setup tasks after deployment to a production environment.
Run this script after deploying your application and running migrations.
"""

import os
import django
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

User = get_user_model()

def create_default_superuser():
    """Create a default superuser if one doesn't exist"""
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating default superuser...")
        username = input("Enter superuser username (default: admin): ") or 'admin'
        email = input("Enter superuser email: ")
        password = input("Enter superuser password: ")
        
        try:
            user = User.objects.create_superuser(username, email, password)
            print(f"Superuser '{username}' created successfully!")
        except Exception as e:
            print(f"Error creating superuser: {e}")
    else:
        print("Superuser already exists.")

def run_initial_setup():
    """Run initial setup tasks"""
    print("Running post-deployment setup...")
    
    # Create default superuser
    create_default_superuser()
    
    # Add any other initial setup tasks here
    print("\nPost-deployment setup completed!")

if __name__ == '__main__':
    run_initial_setup()