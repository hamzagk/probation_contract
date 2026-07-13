import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

def test_email(recipient):
    from django.core.mail import send_mail
    from django.conf import settings
    
    print(f"Testing email functionality for recipient: {recipient}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    
    try:
        send_mail(
            subject='Test Email from HR Portal (Recipient Test)',
            message=f'This is a test email to verify that the email functionality is working for {recipient}.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'muhammad.hamza@giki.edu.pk'),
            recipient_list=[recipient],
            fail_silently=False,
        )
        print(f"SUCCESS: Test email sent successfully to {recipient}!")
    except Exception as e:
        print(f"ERROR: Failed to send email to {recipient} - {str(e)}")

if __name__ == "__main__":
    target = 'muhammad.hamza@giki.edu.pk'
    if len(sys.argv) > 1:
        target = sys.argv[1]
    test_email(target)
