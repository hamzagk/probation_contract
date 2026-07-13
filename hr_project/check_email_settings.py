import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

def check_email_settings():
    from django.conf import settings
    print("=== Email Configuration Check ===")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"EMAIL_HOST_PASSWORD length: {len(getattr(settings, 'EMAIL_HOST_PASSWORD', '')) if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 0}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    
    # Check if password contains spaces
    password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    if ' ' in password:
        print(f"WARNING: Password contains spaces: '{password}'")
        print("This might cause authentication issues.")
        # Try to remove spaces
        clean_password = password.replace(' ', '')
        print(f"Cleaned password length: {len(clean_password)}")
    
    print("\n=== End Email Configuration Check ===")

if __name__ == "__main__":
    check_email_settings()