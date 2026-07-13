#!/usr/bin/env python
"""
Send manual probation expiration list email for FCSE/FCS&E/ITTC departments
To: farhad@giki.edu.pk
CC: muhammad.hamza@giki.edu.pk
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


def send_fcse_probation_email():
    """Send probation report for FCSE/FCS&E/ITTC departments"""
    print("=== Sending FCSE/FCS&E/ITTC Probation Report ===")
    
    # Department names handled by farhad@giki.edu.pk
    fcse_departments = [
        'FCSE', 'FCS&E', 'Faculty of Computer Sciences and Engineering', 
        'Computer Science', 'ITTC', '(ITTC)', 'I.T', 'IT', 'IT Department'
    ]
    
    # Find employees with probation ending within 30 days (includes recently ended)
    past_date = date.today() - timedelta(days=15)
    future_date = date.today() + timedelta(days=30)
    
    employees_queryset = Employee.objects.filter(
        department__name__in=fcse_departments,
        end_date__range=[past_date, future_date],
        probation_status__in=['Active', 'Ending Soon', 'Completed']
    ).order_by('end_date')
    
    if not employees_queryset.exists():
        print("No FCSE/FCS&E/ITTC employees found with probation ending within 30 days.")
        # Check all employees in these departments
        all_fcse = Employee.objects.filter(department__name__in=fcse_departments)
        print(f"Total FCSE/FCS&E/ITTC employees in database: {all_fcse.count()}")
        if all_fcse.exists():
            print("\nAll FCSE/FCS&E/ITTC employees:")
            for emp in all_fcse:
                print(f"  - {emp.name} ({emp.employee_id}) - {emp.designation}")
                print(f"    Start: {emp.start_date}, End: {emp.end_date}, Status: {emp.probation_status}")
        return
    
    print(f"Found {employees_queryset.count()} employee(s) with probation ending soon")
    print()
    
    # Build employee list
    employees = []
    for emp in employees_queryset:
        dept_name = emp.department.name if emp.department else 'N/A'
        days_left = (emp.end_date - date.today()).days
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
        print(f"  - {emp.name} ({emp_data['id']}) - {emp.designation} ({dept_name})")
        print(f"    Probation ends: {emp_data['end_date']} ({days_left} days)")
    
    print()
    
    # Prepare email context
    context = {
        'employees': employees,
        'current_date': date.today().strftime('%B %d, %Y'),
        'report_title': 'Probation Report: FCSE/FCS&E/ITTC',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        'report_period': 'Next 30 days',
        'department_name': 'FCSE/FCS&E/ITTC (Faculty of Computer Sciences & IT)',
    }
    
    # Render HTML email template
    try:
        html_message = render_to_string('hr_portal/probation_report_email.html', context)
        print("[OK] Email template rendered successfully")
    except Exception as e:
        print(f"[ERROR] Error rendering template: {e}")
        return
    
    # Email recipients
    to_email = ['farhad@giki.edu.pk']  # FCSE/FCS&E/ITTC contact
    cc_email = ['muhammad.hamza@giki.edu.pk']  # CC to Muhammad Hamza
    
    subject = f"Probation Report: FCSE/FCS&E/ITTC - {len(employees)} Employee(s) ({date.today().strftime('%B %d, %Y')})"
    
    print(f"\nTo: {to_email}")
    print(f"CC: {cc_email}")
    print(f"Subject: {subject}")
    print()
    
    # Create and send email
    email = EmailMultiAlternatives(
        subject=subject,
        body=f"This is an HTML email report containing a list of FCSE/FCS&E/ITTC employees whose probation periods are ending soon (within the next 30 days). Please view it in a compatible email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_email,
        cc=cc_email
    )
    email.attach_alternative(html_message, "text/html")
    
    try:
        email.send()
        print("[OK] SUCCESS: Email sent to FCSE/FCS&E/ITTC with CC to Muhammad Hamza")
        print(f"\nEmployee details sent ({len(employees)}):")
        for emp in employees:
            print(f"  - {emp['name']} ({emp['id']}) - {emp['designation']} ({emp['department']})")
            print(f"    Probation ends: {emp['end_date']} ({emp['days_until_probation_end']} days)")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


if __name__ == '__main__':
    send_fcse_probation_email()
