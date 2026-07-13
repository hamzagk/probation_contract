import os
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from hr_portal.models import Employee

def send_manual_probation_report():
    """Send manual probation report to specified email addresses"""
    print("=== Sending Manual Probation Report ===")

    # Find employees with probation ending within 30 days (one month)
    future_date = date.today() + timedelta(days=30)
    employees_queryset = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon']
    ).order_by('end_date')

    if not employees_queryset.exists():
        print("No employees found with probation ending within 30 days.")
        return

    print(f"Found {employees_queryset.count()} employees with probation ending within 30 days")

    # Prepare employee data
    employees = []
    for emp in employees_queryset:
        # Calculate days until probation ends
        days_left = (emp.end_date - date.today()).days

        # Calculate probation completion percentage
        total_probation_days = 180  # Assuming 6 months probation (approx.)
        days_completed = total_probation_days - days_left
        progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

        emp_data = {
            'id': emp.employee_id,
            'name': emp.name,
            'designation': emp.designation,
            'department': emp.department.name if emp.department else 'N/A',
            'start_date': emp.start_date.strftime('%B %d, %Y'),
            'end_date': emp.end_date.strftime('%B %d, %Y'),
            'days_until_probation_end': days_left,
            'probation_completion_percent': progress_percentage,
        }
        employees.append(emp_data)

    # Prepare context for email template
    context = {
        'employees': employees,
        'current_date': date.today().strftime('%B %d, %Y'),
        'report_title': 'Monthly Probation Report: Employees with Ending Probation',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        'report_period': 'Next 30 days'
    }

    # Render HTML email template
    html_message = render_to_string('hr_portal/probation_report_email.html', context)

    # Define recipient email addresses - Updated to requested addresses
    recipient_emails = [
        'muhammad.hamza@giki.edu.pk',
        'muhammad.hamza@giki.edu.pk'
    ]

    # Create and send the email
    subject = f"Monthly Probation Report: {len(employees)} Employees with Ending Probation ({date.today().strftime('%B %d, %Y')})"

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"This is an HTML email report containing a list of employees whose probation periods are ending soon (within the next 30 days). Please view it in a compatible email client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        print(f"SUCCESS: Probation report sent to {len(recipient_emails)} recipients")
        print(f"Report contains {len(employees)} employees")
        print(f"Recipients: {', '.join(recipient_emails)}")

        # Print details of employees in the report
        print("\nEmployees in the report:")
        for emp in employees:
            print(f"- {emp['name']} (ID: {emp['id']}) - {emp['designation']} - {emp['department']} - Ends: {emp['end_date']} ({emp['days_until_probation_end']} days)")

    except Exception as e:
        print(f"ERROR: Failed to send email - {str(e)}")

if __name__ == "__main__":
    send_manual_probation_report()