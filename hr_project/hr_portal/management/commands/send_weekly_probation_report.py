from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date, timedelta
from hr_portal.models import Employee
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send automatic probation report to HR members every Tuesday'

    def handle(self, *args, **options):
        self.stdout.write('Starting automatic probation report...')

        # Find employees with probation ending within 20 days - exclude Associate Professors
        future_date = date.today() + timedelta(days=20)
        employees_queryset = Employee.objects.filter(
            end_date__range=[date.today(), future_date],
            probation_status__in=['Active', 'Ending Soon']
        ).exclude(designation__icontains='Associate Professor')

        if not employees_queryset.exists():
            self.stdout.write(
                self.style.WARNING('No employees found with probation ending within 20 days.')
            )
            return

        self.stdout.write(
            f'Found {employees_queryset.count()} employees with probation ending within 20 days'
        )

        # Prepare employee data
        employees = []
        for emp in employees_queryset:
            # Calculate days until probation ends
            days_left = (emp.end_date - date.today()).days

            # Calculate probation completion percentage
            total_probation_days = 180  # Assuming 6 months probation (approx.)
            days_completed = total_probation_days - days_left
            progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

            emp_id = str(emp.employee_id)
            if emp_id.endswith('.0'):
                emp_id = emp_id[:-2]

            emp_data = {
                'id': emp_id,  # Fixed to remove trailing .0
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
            'report_title': 'Weekly Probation Report: Employees with Ending Probation',
            'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
            'report_period': 'Next 20 days'
        }

        # Render HTML email template
        html_message = render_to_string('hr_portal/probation_report_email.html', context)

        # Define recipient email addresses
        recipient_emails = [
            'muhammad.hamza@giki.edu.pk',
            'muhammad.hamza@giki.edu.pk'
        ]

        # Create and send the email
        subject = f"Weekly Probation Report: {len(employees)} Employees with Ending Probation ({date.today().strftime('%B %d, %Y')})"

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"This is an HTML email report containing a list of employees whose probation periods are ending soon (within the next 30 days). Please view it in a compatible email client.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_emails
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            self.stdout.write(
                self.style.SUCCESS(
                    f'SUCCESS: Probation report sent to {len(recipient_emails)} recipients. '
                    f'Report contains {len(employees)} employees.'
                )
            )

            logger.info(f'Automatic probation report sent successfully to {len(recipient_emails)} recipients')

        except Exception as e:
            error_msg = f'ERROR: Failed to send automatic probation report - {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg, exc_info=True)

        self.stdout.write('Automatic probation report process completed.')