#!/usr/bin/env python
"""
Send Manual Probation Report to Specific Department Contact
"""
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


def send_manual_probation_to_contact(to_email, cc_email, departments):
    """Send manual probation report to specific contact"""
    print(f"=== Sending Manual Probation Report ===")
    print(f"To: {to_email}")
    print(f"CC: {cc_email}")
    print(f"Departments: {', '.join(departments)}")
    print()

    # Find employees with probation ending within 30 days from specified departments
    future_date = date.today() + timedelta(days=30)
    
    employees_queryset = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon'],
        department__name__in=departments
    ).order_by('department__name', 'end_date')

    if not employees_queryset.exists():
        print("No employees found with probation ending within 30 days.")
        return

    print(f"Found {employees_queryset.count()} employees with probation ending within 30 days")
    print()

    # Prepare employee data
    employees = []
    for emp in employees_queryset:
        dept_name = emp.department.name if emp.department else 'N/A'
        
        # Calculate days until probation ends
        days_left = (emp.end_date - date.today()).days
        
        # Calculate probation completion percentage
        total_probation_days = 180
        days_completed = total_probation_days - days_left
        progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0
        
        emp_data = {
            'id': str(emp.employee_id).rstrip('.0') if str(emp.employee_id).endswith('.0') else str(emp.employee_id),
            'name': emp.name,
            'designation': emp.designation,
            'department': dept_name,
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
        'report_title': f'Probation Report: {", ".join(departments)}',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        'report_period': 'Next 30 days',
        'department_name': ', '.join(departments),
    }

    # Render HTML email template
    try:
        html_message = render_to_string('hr_portal/probation_report_email.html', context)
    except Exception as e:
        print(f"[ERROR] Error rendering template: {str(e)}")
        return

    # Create and send the email
    subject = f"Probation Report: {', '.join(departments)} - {len(employees)} Employee(s) ({date.today().strftime('%B %d, %Y')})"

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"This is an HTML email report containing a list of employees from {', '.join(departments)} whose probation periods are ending soon (within the next 30 days). Please view it in a compatible email client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            cc=[cc_email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        print(f"[OK] SUCCESS: Probation report sent successfully")
        print()
        print("Employees in the report:")
        print("-" * 80)
        
        # Group by department for display
        from collections import defaultdict
        by_dept = defaultdict(list)
        for emp in employees:
            by_dept[emp['department']].append(emp)
        
        for dept in sorted(by_dept.keys()):
            print(f"\n{dept}:")
            for emp in by_dept[dept]:
                print(f"  - {emp['name']} ({emp['id']}) - {emp['designation']} - Ends: {emp['end_date']} ({emp['days_until_probation_end']} days)")
        
        print()
        print("=" * 80)
        print(f"Total: {len(employees)} employees across {len(by_dept)} departments")
        print("=" * 80)

    except Exception as e:
        print(f"[ERROR] Failed to send email - {str(e)}")


if __name__ == "__main__":
    # Send to Farhad Gul for FCSE, FCS&E, ITTC departments
    send_manual_probation_to_contact(
        to_email='farhad@giki.edu.pk',
        cc_email='muhammad.hamza@giki.edu.pk',
        departments=['FCSE', 'FCS&E', 'ITTC']
    )
