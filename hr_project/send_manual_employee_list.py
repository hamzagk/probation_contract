"""
Script to manually send employee list to specified email
"""
import os
import sys
import django
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from datetime import date, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def send_employee_list_to_email(email_recipient):
    """Send employee list to specified email"""
    
    # Get all employees
    employees_queryset = Employee.objects.all().order_by('end_date')

    if not employees_queryset.exists():
        print('No employees found in the system.')
        return False

    # Prepare employee data with additional computed fields for the template
    employees = []
    for emp in employees_queryset:
        # Calculate probation progress percentage
        total_probation_days = 180  # Assuming 6 months probation (approx.)
        days_completed = total_probation_days - emp.days_until_probation_end
        progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

        # Create a dict with all the properties needed for the template
        # Remove trailing .0 from employee ID if present
        emp_id = str(emp.employee_id)
        if emp_id.endswith('.0'):
            emp_id = emp_id.rstrip('.0')

        emp_data = {
            'id': emp_id,  # Fixed to remove trailing .0
            'name': emp.name,
            'designation': emp.designation,
            'department': emp.department,
            'start_date': emp.start_date.strftime('%B %d, %Y'),
            'end_date': emp.end_date.strftime('%B %d, %Y'),
            'days_until_probation_end': emp.days_until_probation_end,
            'probation_completion_percent': emp.probation_completion_percent,
            'probation_status': emp.probation_status,
        }
        employees.append(emp_data)

    # Prepare context for the email template
    context = {
        'employees': employees,
        'current_date': date.today().strftime('%B %d, %Y'),
        'report_title': 'Complete Employee List',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        'total_employees': len(employees),
    }

    # Render the HTML email template
    html_message = render_to_string('hr_portal/probation_report_email.html', context)

    # Create and send the email
    subject = f"Complete Employee List Report ({date.today().strftime('%B %d, %Y')}) - {len(employees)} Employees"

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"This is an HTML email report containing a complete list of all employees in the system. Please view it in a compatible email client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_recipient]  # Send to specified recipient
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        print(f'Employee list sent successfully to {email_recipient}. Report contains {len(employees)} employees.')
        return True
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return False

if __name__ == "__main__":
    # Send to the specified email
    recipient_email = "muhammad.hamza@giki.edu.pk"
    success = send_employee_list_to_email(recipient_email)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")