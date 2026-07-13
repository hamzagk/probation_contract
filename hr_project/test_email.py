import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

def test_email():
    from django.core.mail import send_mail
    from django.conf import settings
    
    print("Testing email functionality...")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    
    try:
        send_mail(
            subject='Test Email from HR Portal',
            message='This is a test email to verify that the email functionality is working properly.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'muhammad.hamza@giki.edu.pk'),
            recipient_list=['muhammad.hamza@giki.edu.pk'],
            fail_silently=False,
        )
        print("SUCCESS: Test email sent successfully!")
    except Exception as e:
        print(f"ERROR: Failed to send email - {str(e)}")
        print("This could be due to incorrect app password or Gmail security settings.")

if __name__ == "__main__":
    test_email()