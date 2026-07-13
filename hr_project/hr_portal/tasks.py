from celery import shared_task
from django.core.management import call_command
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import date, timedelta

@shared_task
def check_probation_expirations():
    """Celery task to check probation expirations and send notifications"""
    call_command('send_probation_notifications')


@shared_task
def send_probation_notifications_task():
    """
    Celery task to send automatic email notifications for employees with less than 15 days remaining in probation
    Excludes Associate Professors (they don't have probation)
    """
    from hr_portal.models import Employee, ProbationNotification

    # Find employees with less than 15 days remaining in probation (exclude Associate Professors)
    future_date = date.today() + timedelta(days=15)
    employees = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon']
    ).exclude(designation__icontains='Associate Professor')

    results = []
    for employee in employees:
        # Check if a notification has already been sent for this employee today
        if not ProbationNotification.objects.filter(
            employee=employee,
            notification_date__date=date.today(),
            notification_type='automatic_email'
        ).exists():

            # Calculate probation progress percentage
            total_probation_days = 180  # Assuming 6 months probation (approx.)
            days_completed = total_probation_days - employee.days_until_probation_end
            progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

            # Prepare context for the email template
            context = {
                'employee_name': employee.name,
                'employee_id': employee.employee_id,
                'employee_designation': employee.designation,
                'employee_department': employee.department,
                'employee_start_date': employee.start_date.strftime('%B %d, %Y'),
                'employee_end_date': employee.end_date.strftime('%B %d, %Y'),
                'days_until_probation_end': employee.days_until_probation_end,
                'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
                'progress_percentage': progress_percentage,
            }

            # Render the HTML email template
            html_message = render_to_string('hr_portal/enhanced_probation_notification_email.html', context)

            # Determine recipient email - default to muhammad.hamza@giki.edu.pk
            recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')

            # If department has an email, use that instead
            if (employee.department and
                hasattr(employee.department, 'email') and
                employee.department.email):
                recipient_email = employee.department.email
            else:
                # Use the default HR email from settings
                recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')

            # List of additional HR members to CC
            hr_cc_emails = [
                'hikmatullah@giki.edu.pk',
                'nasirali@giki.edu.pk',
                'saboor@giki.edu.pk',
                'israr.hassan@giki.edu.pk',
                'shahid@giki.edu.pk'
            ]

            # Add the main HR contact to CC list
            main_hr = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
            if main_hr not in hr_cc_emails:
                hr_cc_emails.insert(0, main_hr)

            # Create and send the email with CC to HR
            subject = f"Automatic Alert: Probation Period Ending Soon for {employee.name} ({employee.employee_id})"

            email = EmailMultiAlternatives(
                subject=subject,
                body=f"This is an HTML email notification about {employee.name}'s probation period. Please view it in a compatible email client.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],  # Primary recipient is the department
                cc=hr_cc_emails  # CC to main HR and additional HR members
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            # Create a notification record
            ProbationNotification.objects.create(
                employee=employee,
                days_before_expiry=employee.days_until_probation_end,
                sent=True,
                notification_type='automatic_email'
            )

            results.append(f'Successfully sent automatic notification for {employee.name}')
        else:
            results.append(f'Notification already sent today for {employee.name}')

    if not employees:
        results.append('No employees found with less than 15 days remaining in probation')

    return results


@shared_task
def send_weekly_employees_report():
    """
    Celery task to send a weekly report of employees with ending probation to all HR members
    Runs every Tuesday as configured in settings
    Excludes Associate Professors (they don't have probation)
    """
    from hr_portal.models import Employee

    # Find employees with less than 30 days remaining in probation (exclude Associate Professors)
    future_date = date.today() + timedelta(days=30)
    employees_queryset = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon']
    ).exclude(designation__icontains='Associate Professor')

    # Prepare employee data with additional computed fields for the template
    employees = []
    for emp in employees_queryset:
        # Calculate probation progress percentage
        total_probation_days = 180  # Assuming 6 months probation (approx.)
        days_completed = total_probation_days - emp.days_until_probation_end
        progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

        # Create a dict with all the properties needed for the template
        emp_data = {
            'id': emp.employee_id,
            'name': emp.name,
            'designation': emp.designation,
            'department': emp.department,
            'start_date': emp.start_date.strftime('%B %d, %Y'),
            'end_date': emp.end_date.strftime('%B %d, %Y'),
            'days_until_probation_end': emp.days_until_probation_end,
            'probation_completion_percent': emp.probation_completion_percent,
        }
        employees.append(emp_data)

    # Prepare context for the email template
    context = {
        'employees': employees,
        'current_date': date.today().strftime('%B %d, %Y'),
        'report_title': 'Weekly Probation Report',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
    }

    # Render the HTML email template
    html_message = render_to_string('hr_portal/probation_report_email.html', context)

    # List of HR members to send the email to
    hr_emails = [
        'muhammad.hamza@giki.edu.pk',
        'muhammad.hamza@giki.edu.pk',
        'hikmatullah@giki.edu.pk',
        'nasirali@giki.edu.pk',
        'saboor@giki.edu.pk',
        'israr.hassan@giki.edu.pk',
        'shahid@giki.edu.pk'
    ]

    # Add the main HR contact if it's not already in the list
    main_hr = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
    if main_hr not in hr_emails:
        hr_emails.insert(0, main_hr)

    # Create and send the email to all HR members
    subject = f"Weekly Probation Report: {len(employees)} Employees with Ending Probation ({date.today().strftime('%B %d, %Y')})"

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"This is an HTML email report containing a list of employees whose probation periods are ending soon. Please view it in a compatible email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=hr_emails  # Send to all HR members
    )
    email.attach_alternative(html_message, "text/html")
    email.send()

    results = [f'Weekly probation report sent successfully to {len(hr_emails)} HR members. Report contains {len(employees)} employees.']

    if not employees:
        results.append('No employees found with less than 30 days remaining in probation')

    return results


@shared_task
def send_weekly_probation_report_task():
    """Celery task to send weekly probation report via management command"""
    from django.core.management import call_command
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Call the management command to send the weekly probation report
        call_command('send_weekly_probation_report', verbosity=0)
        logger.info("Weekly probation report task completed successfully")
        return "Weekly probation report task completed successfully"
    except Exception as e:
        error_msg = f"Error in weekly probation report task: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


@shared_task
def send_monthly_probation_reports_task(test_recipient=None, force=False):
    """Celery task to send department-wise monthly probation reports."""
    from hr_portal.monthly_probation_reports import send_monthly_probation_reports
    import logging

    logger = logging.getLogger(__name__)

    try:
        result = send_monthly_probation_reports(
            test_recipient=test_recipient,
            force=force,
        )
        logger.info(
            "Monthly probation report task completed: %s report(s) sent, %s skipped",
            result['sent_reports'],
            result['skipped_reports'],
        )
        return result
    except Exception as e:
        error_msg = f"Error in monthly probation report task: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {'error': error_msg}

@shared_task
def send_contract_expiration_notifications_task():
    """
    Celery task to send automatic email notifications for employees with less than 60 days remaining in contract
    Excludes Associate Professors? (They might have contracts too, but we'll include all for now)
    """
    from hr_portal.models import Employee
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    from datetime import date, timedelta
    from django.template.loader import render_to_string

    # Find employees with less than 60 days remaining in contract
    future_date = date.today() + timedelta(days=60)
    employees = Employee.objects.filter(
        contract_end_date__range=[date.today(), future_date],
        contract_status__in=['active', 'expiring_soon']
    ).exclude(contract_start_date=None)  # Ensure they have a contract start date

    results = []
    for employee in employees:
        # We'll create a simple notification record if we had a model, but for now just send email
        # Prepare context for the email template
        context = {
            'employee_name': employee.name,
            'employee_id': employee.employee_id,
            'employee_designation': employee.designation,
            'employee_department': employee.department,
            'employee_contract_start_date': employee.contract_start_date.strftime('%B %d, %Y'),
            'employee_contract_end_date': employee.contract_end_date.strftime('%B %d, %Y'),
            'days_until_contract_end': employee.days_until_contract_end,
            'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        }

        # We'll try to use a template if it exists, otherwise fallback to a simple message
        try:
            html_message = render_to_string('hr_portal/contract_expiration_email.html', context)
        except:
            # Fallback to a simple text message
            html_message = f"""
            <html>
            <body>
                <h2>Contract Expiration Notification</h2>
                <p>Dear {employee.name},</p>
                <p>This is a notification that your contract is ending soon.</p>
                <p>Details:</p>
                <ul>
                    <li>Employee ID: {employee.employee_id}</li>
                    <li>Designation: {employee.designation}</li>
                    <li>Department: {employee.department}</li>
                    <li>Contract Start Date: {employee.contract_start_date.strftime('%B %d, %Y')}</li>
                    <li>Contract End Date: {employee.contract_end_date.strftime('%B %d, %Y')}</li>
                    <li>Days Until Contract End: {employee.days_until_contract_end}</li>
                </ul>
                <p>Please contact HR for renewal or further instructions.</p>
            </body>
            </html>
            """

        # Determine recipient email - default to muhammad.hamza@giki.edu.pk
        recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')

        # If department has an email, use that instead
        if (employee.department and
            hasattr(employee.department, 'email') and
            employee.department.email):
            recipient_email = employee.department.email
        else:
            # Use the default HR email from settings
            recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')

        # List of additional HR members to CC
        hr_cc_emails = [
            'hikmatullah@giki.edu.pk',
            'nasirali@giki.edu.pk',
            'saboor@giki.edu.pk',
            'israr.hassan@giki.edu.pk',
            'shahid@giki.edu.pk'
        ]

        # Add the main HR contact to CC list
        main_hr = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
        if main_hr not in hr_cc_emails:
            hr_cc_emails.insert(0, main_hr)

        # Create and send the email with CC to HR
        subject = f"Automatic Alert: Contract Ending Soon for {employee.name} ({employee.employee_id})"

        email = EmailMultiAlternatives(
            subject=subject,
            body=f"This is an HTML email notification about {employee.name}'s contract expiration. Please view it in a compatible email client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],  # Primary recipient is the department
            cc=hr_cc_emails  # CC to main HR and additional HR members
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        results.append(f'Successfully sent contract expiration notification for {employee.name}')
    if not employees:
        results.append('No employees found with less than 60 days remaining in contract')
    return results
