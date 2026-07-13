import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

def test_email_with_correct_password():
    from django.conf import settings
    from django.core.mail import get_connection
    
    print("=== Testing Email Connection ===")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD length: {len(settings.EMAIL_HOST_PASSWORD)}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
    
    # Check if password has the correct format (16 chars with spaces = 19 chars total)
    password = settings.EMAIL_HOST_PASSWORD
    if len(password) == 19 and password.count(' ') == 3:
        print("Password appears to have spaces in the correct format (4 groups of 4 chars)")
        # Try to connect with the password as-is
    elif len(password) == 16 and ' ' not in password:
        print("Password appears to be in clean format (16 chars without spaces)")
    else:
        print(f"Password format unexpected: length={len(password)}, spaces={password.count(' ')}")
    
    try:
        # Test connection
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,  # This is the critical part
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        # Try to open connection
        connection.open()
        print("SUCCESS: Email connection opened successfully!")
        connection.close()
        return True
    except Exception as e:
        print(f"ERROR: Failed to open email connection - {str(e)}")
        return False

if __name__ == "__main__":
    test_email_with_correct_password()