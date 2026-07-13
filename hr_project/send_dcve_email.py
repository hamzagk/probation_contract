#!/usr/bin/env python
"""
Send manual email about DCvE (Department of Civil Engineering) to muhammad.hamza@giki.edu.pk
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_dcve_email():
    subject = "DCvE (Department of Civil Engineering) - HR Portal Information"
    
    body = """Dear Muhammad Hamza,

This is a manual email regarding DCvE (Department of Civil Engineering).

Department Details:
- Department Code: DCvE
- Department Name: Department of Civil Engineering
- Primary Contact: sehrish.mazhar@giki.edu.pk

This email was sent from the HR Portal system.

Best regards,
HR Portal System
"""
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['muhammad.hamza@giki.edu.pk']
    
    try:
        send_mail(
            subject,
            body,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        print(f"[OK] Email sent successfully to {recipient_list}")
        print(f"  Subject: {subject}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False
    
    return True

if __name__ == '__main__':
    send_dcve_email()
