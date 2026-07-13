#!/usr/bin/env python
"""
Combined All-Departments Probation Report Email Script (Test)
Sends a single combined report to muhammad.hamza@giki.edu.pk
Excludes Associate Professors (probation is from Assistant Professor onwards)
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


def send_all_departments_combined_test():
    """Send combined probation report for all departments to test email"""
    print("=== Sending Combined All-Departments Probation Report (Test) ===")
    print()

    # Find employees with probation ending within 30 days (one month)
    # Starting from Ms. Bakhtawar Rubab (Feb 20, 2026 onwards)
    start_date_filter = date(2026, 2, 20)  # Ms. Bakhtawar Rubab's end date
    future_date = date.today() + timedelta(days=30)
    
    employees_queryset = Employee.objects.filter(
        end_date__range=[start_date_filter, future_date],
        probation_status__in=['Active', 'Ending Soon']
    ).order_by('department__name', 'end_date')

    if not employees_queryset.exists():
        print("No employees found with probation ending within 30 days from the specified date.")
        return

    print(f"Found {employees_queryset.count()} employees with probation ending within 30 days")
    print()

    # Prepare employee data (excluding Associate Professors)
    employees = []
    excluded_count = 0
    
    for emp in employees_queryset:
        # Skip Associate Professors
        if 'Associate Professor' in emp.designation:
            excluded_count += 1
            print(f"  [EXCLUDED] {emp.name} - {emp.designation} ({emp.department.name if emp.department else 'N/A'})")
            continue
        
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

    print()
    print(f"Total employees in report: {len(employees)}")
    print(f"Excluded (Associate Professors): {excluded_count}")
    print()

    if not employees:
        print("No employees to include in the report after filtering.")
        return

    # Prepare context for email template
    context = {
        'employees': employees,
        'current_date': date.today().strftime('%B %d, %Y'),
        'report_title': 'Combined Probation Report: All Departments',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        'report_period': 'Next 30 days',
        'department_name': 'All Departments',
    }

    # Render HTML email template
    try:
        html_message = render_to_string('hr_portal/probation_report_email.html', context)
    except Exception as e:
        print(f"[ERROR] Error rendering template: {str(e)}")
        return

    # Test recipient
    recipient_email = 'muhammad.hamza@giki.edu.pk'
    subject = f"[TEST] Combined Probation Report: All Departments - {len(employees)} Employee(s) ({date.today().strftime('%B %d, %Y')})"

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"This is an HTML email report containing a combined list of employees from ALL departments whose probation periods are ending soon (within the next 30 days). Associate Professors have been excluded from this report. Please view it in a compatible email client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        print(f"[OK] SUCCESS: Combined report sent to {recipient_email}")
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
    send_all_departments_combined_test()
