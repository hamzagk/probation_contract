from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from datetime import date, timedelta
from hr_portal.models import Employee, ProbationNotification


class Command(BaseCommand):
    help = 'Send automatic email notifications for employees with less than 20 days remaining in probation'

    def handle(self, *args, **options):
        # Find employees with less than 20 days remaining in probation
        # This includes employees whose probation ends within the next 20 days
        future_date = date.today() + timedelta(days=20)
        employees = Employee.objects.filter(
            end_date__range=[date.today(), future_date],
            probation_status__in=['Active', 'Ending Soon']
        )

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
                    to=[recipient_email],
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

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully sent automatic notification for {employee.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Notification already sent today for {employee.name}')
                )

        if not employees:
            self.stdout.write(
                self.style.WARNING('No employees found with less than 15 days remaining in probation')
            )