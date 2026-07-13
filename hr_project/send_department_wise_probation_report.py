#!/usr/bin/env python
"""
Department-wise Probation Report Email Script
Sends separate probation reports to each department's concerned contact person.
"""
import os
import django
from datetime import date, timedelta
from collections import defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from hr_portal.models import Employee

# Department-wise email contacts (permanent list)
# Based on official department contact assignments
DEPARTMENT_CONTACTS = {
    # Department of Chemical Engineering / DChE
    'DChE': ['asad@giki.edu.pk'],
    'Department of Chemical Engineering': ['asad@giki.edu.pk'],
    
    # Faculty of Computer Sciences and Engineering / FCSE / FCS&E - Farhad Gul
    'FCSE': ['farhad@giki.edu.pk'],
    'Faculty of Computer Sciences and Engineering': ['farhad@giki.edu.pk'],
    'FCS&E': ['farhad@giki.edu.pk'],
    'Computer Science': ['farhad@giki.edu.pk'],
    
    # Faculty of Electrical Engineering / FEE
    'FEE': ['ikramullah@giki.edu.pk'],
    'Faculty of Electrical Engineering': ['ikramullah@giki.edu.pk'],
    'Electrical Engineering': ['ikramullah@giki.edu.pk'],
    
    # Faculty of Materials and Chemical Engineering / FMCE / FM&CE
    'FMCE': ['mohajir@giki.edu.pk'],
    'Faculty of Materials and Chemical Engineering': ['mohajir@giki.edu.pk'],
    'FM&CE': ['mohajir@giki.edu.pk'],
    ',FMCE': ['mohajir@giki.edu.pk'],
    
    # Faculty of Engineering Sciences / FES - Muhammad Shafiq
    'FES': ['shafiq@giki.edu.pk'],
    'Faculty of Engineering Sciences': ['shafiq@giki.edu.pk'],
    'Faculty of basic sciences': ['shafiq@giki.edu.pk'],
    
    # School of Management Sciences / SMgS
    'SMgS': ['bashar@giki.edu.pk'],
    'School of Management Sciences': ['bashar@giki.edu.pk'],
    'School management sciences': ['bashar@giki.edu.pk'],
    
    # Department of Civil Engineering / DCvE
    'DCvE': ['sehrish.mazhar@giki.edu.pk'],
    'Department of Civil Engineering': ['sehrish.mazhar@giki.edu.pk'],
    
    # Faculty of Mechanical Engineering / FME
    'FME': ['mohajir@giki.edu.pk'],  # PS to Dean FMCE (covers FMCE faculty)
    'Mechanical Engineering': ['mohajir@giki.edu.pk'],
    
    # ITTC / I.T / IT - Farhad Gul
    'ITTC': ['farhad@giki.edu.pk'],
    '(ITTC)': ['farhad@giki.edu.pk'],
    'I.T': ['farhad@giki.edu.pk'],
    'IT': ['farhad@giki.edu.pk'],
    'IT Department': ['farhad@giki.edu.pk'],
    
    # FBS (Faculty of Basic Sciences) - Muhammad Shafiq
    'FBS': ['shafiq@giki.edu.pk'],  # Faculty of basic sciences
    'Biology': ['shafiq@giki.edu.pk'],
    'Mathematics': ['shafiq@giki.edu.pk'],
    'Physics': ['shafiq@giki.edu.pk'],
    'Chemistry': ['shafiq@giki.edu.pk'],
    'Humanities': ['shafiq@giki.edu.pk'],
    'FBS/FES': ['shafiq@giki.edu.pk'],
    
    # GIK College - Jamil
    'GIK College': ['jamil@giki.edu.pk'],
    
    # MC / Medical Centre / GIK M.C
    'MC': ['nizakat@giki.edu.pk'],
    'Medical Centre': ['nizakat@giki.edu.pk'],
    'GIK M.C': ['nizakat@giki.edu.pk'],
    
    # Procurement - Farid Wahid
    'Procurement': ['farid.wahid@giki.edu.pk'],
    
    # Works & Maintenance / W&M - Director Engineering Projects
    'Work & Maintenance': ['director.engineeringprojects@giki.edu.pk'],
    'W&M': ['director.engineeringprojects@giki.edu.pk'],
    'Transport Section': ['director.engineeringprojects@giki.edu.pk'],
    'Hostels': ['director.engineeringprojects@giki.edu.pk'],
    'Sport Section': ['director.engineeringprojects@giki.edu.pk'],
    'Sports': ['director.engineeringprojects@giki.edu.pk'],
    
    # Default contacts for unmapped departments (Nizakat Ali Khan)
    'N/A': ['nizakat@giki.edu.pk'],
    'Other': ['nizakat@giki.edu.pk'],
    'Admin': ['nizakat@giki.edu.pk'],
    'HR': ['nizakat@giki.edu.pk'],
    'Finance': ['nizakat@giki.edu.pk'],
    'Admission': ['nizakat@giki.edu.pk'],
    'ORIC': ['nizakat@giki.edu.pk'],
    'S&P': ['nizakat@giki.edu.pk'],
    'SOPREST': ['nizakat@giki.edu.pk'],
    'Main Store': ['nizakat@giki.edu.pk'],
    'Marketing': ['nizakat@giki.edu.pk'],
    'Student Affairs': ['nizakat@giki.edu.pk'],
    'Facilitation': ['nizakat@giki.edu.pk'],
    'A&E': ['nizakat@giki.edu.pk'],
    'Rector': ['nizakat@giki.edu.pk'],
    'Pro-Rector (Admin)': ['nizakat@giki.edu.pk'],
    'Pro-Rector (Academic)': ['nizakat@giki.edu.pk'],
}

# Department name aliases for normalization (handles variations in DB)
DEPARTMENT_ALIASES = {
    '(ITTC)': 'ITTC',
    ',FMCE': 'FMCE',
    ',FME': 'FME',
    'FCS&E': 'FCS&E',
    'G IK College': 'GIK College',
    'G IKI': 'GIK College',
}

# Department grouping for combined emails (send combined list to same contact)
DEPARTMENT_GROUPS = {
    'farhad@giki.edu.pk': ['FCSE', 'FCS&E', 'Computer Science', 'Faculty of Computer Sciences and Engineering', 'ITTC', '(ITTC)', 'I.T', 'IT', 'IT Department'],
    'shafiq@giki.edu.pk': ['FES', 'FBS', 'Faculty of Engineering Sciences', 'Faculty of basic sciences', 'Biology', 'Mathematics', 'Physics', 'Chemistry', 'Humanities', 'FBS/FES'],
    'mohajir@giki.edu.pk': ['FMCE', 'FM&CE', ',FMCE', 'FME', 'Mechanical Engineering', 'Faculty of Materials and Chemical Engineering'],
    'bashar@giki.edu.pk': ['SMgS', 'School of Management Sciences', 'School management sciences'],
    'asad@giki.edu.pk': ['DChE', 'Department of Chemical Engineering'],
    'ikramullah@giki.edu.pk': ['FEE', 'Faculty of Electrical Engineering', 'Electrical Engineering'],
    'sehrish.mazhar@giki.edu.pk': ['DCvE', 'Department of Civil Engineering'],
    'jamil@giki.edu.pk': ['GIK College'],
    'farid.wahid@giki.edu.pk': ['Procurement'],
    'director.engineeringprojects@giki.edu.pk': ['Work & Maintenance', 'W&M', 'Transport Section', 'Hostels', 'Sport Section', 'Sports'],
    'nizakat@giki.edu.pk': ['MC', 'Medical Centre', 'GIK M.C', 'N/A', 'Other', 'Admin', 'HR', 'Finance', 'Admission', 'ORIC', 'S&P', 'SOPREST', 'Main Store', 'Marketing', 'Student Affairs', 'Facilitation', 'A&E', 'Rector', 'Pro-Rector (Admin)', 'Pro-Rector (Academic)'],
}

# HR team emails for CC
HR_CC_EMAILS = [
    'muhammad.hamza@giki.edu.pk',
    'nasirali@giki.edu.pk',
    'hikmatullah@giki.edu.pk',
    'shahid@giki.edu.pk',
]

# Test mode configuration
TEST_MODE = True  # Set to False for production
TEST_TO_EMAIL = 'muhammad.hamza@giki.edu.pk'


def send_department_wise_probation_report():
    """Send department-wise probation reports to concerned contacts"""
    print("=== Sending Department-wise Probation Report ===")
    print(f"Test Mode: {'ENABLED' if TEST_MODE else 'DISABLED'}")
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

    # Group employees by contact email (combining departments with same contact)
    contact_groups = defaultdict(lambda: {'employees': [], 'departments': set()})
    
    for emp in employees_queryset:
        raw_dept_name = emp.department.name if emp.department else 'N/A'
        # Normalize department name using aliases
        dept_name = DEPARTMENT_ALIASES.get(raw_dept_name, raw_dept_name)
        
        # Find the contact email for this department
        contact_email = None
        for email, dept_list in DEPARTMENT_GROUPS.items():
            if dept_name in dept_list:
                contact_email = email
                break
        
        # If no group found, use DEPARTMENT_CONTACTS
        if contact_email is None:
            contacts = DEPARTMENT_CONTACTS.get(dept_name, [])
            contact_email = contacts[0] if contacts else None
        
        if contact_email is None:
            print(f"  [WARN] No contact found for {dept_name}. Skipping employee {emp.name}...")
            continue
        
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
        contact_groups[contact_email]['employees'].append(emp_data)
        contact_groups[contact_email]['departments'].add(dept_name)

    # Send email for each contact group
    total_sent = 0
    for contact_email, group_data in contact_groups.items():
        employees = group_data['employees']
        departments = group_data['departments']
        
        # Create a readable department list for the subject
        dept_list_str = ', '.join(sorted(departments))
        print(f"Processing: {dept_list_str} ({len(employees)} employees)")
        print(f"  Contact: {contact_email}")
        
        # Prepare context for email template
        context = {
            'employees': employees,
            'current_date': date.today().strftime('%B %d, %Y'),
            'report_title': f'Probation Report: {dept_list_str}',
            'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
            'report_period': 'Next 30 days',
            'department_name': dept_list_str,
        }
        
        # Render HTML email template
        try:
            html_message = render_to_string('hr_portal/probation_report_email.html', context)
        except Exception as e:
            print(f"  [ERROR] Error rendering template: {str(e)}")
            continue
        
        # Determine recipients based on test mode
        if TEST_MODE:
            recipient_emails = [TEST_TO_EMAIL]
            subject_prefix = "[TEST] "
        else:
            recipient_emails = [contact_email]
            cc_emails = HR_CC_EMAILS
            subject_prefix = ""
        
        # Create and send the email
        subject = f"{subject_prefix}Probation Report: {dept_list_str} - {len(employees)} Employee(s) ({date.today().strftime('%B %d, %Y')})"
        
        try:
            if TEST_MODE:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=f"This is an HTML email report containing a list of employees from {dept_list_str} whose probation periods are ending soon (within the next 30 days). Please view it in a compatible email client.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=recipient_emails
                )
            else:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=f"This is an HTML email report containing a list of employees from {dept_list_str} whose probation periods are ending soon (within the next 30 days). Please view it in a compatible email client.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=recipient_emails,
                    cc=cc_emails
                )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            print(f"  [OK] SUCCESS: Sent to {len(recipient_emails)} recipient(s)")
            if not TEST_MODE:
                print(f"    CC: {', '.join(HR_CC_EMAILS)}")
            
            # Print employee details
            print(f"    Employees ({len(employees)}):")
            for emp in employees:
                print(f"      - {emp['name']} ({emp['id']}) - {emp['designation']} ({emp['department']}) - Ends: {emp['end_date']} ({emp['days_until_probation_end']} days)")
            
            total_sent += 1
            
        except Exception as e:
            print(f"  [ERROR] Failed to send email - {str(e)}")
        
        print()

    print("=" * 50)
    print(f"Department-wise Probation Report Complete!")
    print(f"Total contact groups processed: {len(contact_groups)}")
    print(f"Total emails sent: {total_sent}")
    print()

    if TEST_MODE:
        print("[WARN] TEST MODE is ENABLED")
        print("  Emails are being sent to:")
        print(f"    To: {TEST_TO_EMAIL}")
        print()
        print("To send to actual department contacts, set TEST_MODE = False in the script")


if __name__ == "__main__":
    send_department_wise_probation_report()
