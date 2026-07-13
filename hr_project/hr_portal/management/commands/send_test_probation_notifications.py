from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from datetime import date, timedelta
from hr_portal.models import Employee, ProbationNotification


class Command(BaseCommand):
    help = 'Send test email with employees whose probation ends within one month'

    def handle(self, *args, **options):
        # Find employees with probation ending within one month (30 days)
        future_date = date.today() + timedelta(days=30)
        employees = Employee.objects.filter(
            end_date__range=[date.today(), future_date],
            probation_status__in=['Active', 'Ending Soon']
        ).order_by('end_date')

        if not employees:
            self.stdout.write(
                self.style.WARNING('No employees found with probation ending within one month')
            )
            return

        # Prepare context for the email template
        employee_data = []
        for emp in employees:
            total_probation_days = 180  # Assuming 6 months probation (approx.)
            days_completed = total_probation_days - emp.days_until_probation_end
            progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0
            
            employee_data.append({
                'name': emp.name,
                'id': emp.employee_id,
                'designation': emp.designation,
                'department': emp.department.name if emp.department else 'Unassigned',
                'start_date': emp.start_date.strftime('%B %d, %Y'),
                'end_date': emp.end_date.strftime('%B %d, %Y'),
                'days_remaining': emp.days_until_probation_end,
                'progress_percentage': progress_percentage
            })

        context = {
            'employees': employee_data,
            'report_date': date.today().strftime('%B %d, %Y'),
            'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        }

        # Render the HTML email template
        html_message = render_to_string('hr_portal/probation_report_email.html', context)

        # Send to the HR email
        recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
        
        subject = f"Test Probation Report: {len(employees)} Employees with Probation Ending Within One Month"

        # List of additional HR members to CC
        hr_cc_emails = [
            'hikmatullah@giki.edu.pk',
            'nasirali@giki.edu.pk',
            'saboor@giki.edu.pk',
            'israr.hassan@giki.edu.pk',
            'shahid@giki.edu.pk'
        ]

        email = EmailMultiAlternatives(
            subject=subject,
            body=f"This is a test report showing employees whose probation ends within one month. Please view it in a compatible email client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
            cc=hr_cc_emails  # CC additional HR members
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent test report with {len(employees)} employees to {recipient_email}')
        )