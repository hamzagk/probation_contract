import os
import sys
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from hr_portal.tasks import (
    send_monthly_probation_reports_task,
    send_probation_notifications_task,
    send_weekly_employees_report,
)


class Command(BaseCommand):
    help = 'Run automatic email notifications for probation expirations (Windows-compatible)'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'Starting automatic email notifications at {datetime.now()}')
        )
        
        # Send daily probation notifications
        self.stdout.write('Sending daily probation notifications...')
        try:
            result = send_probation_notifications_task()
            self.stdout.write(
                self.style.SUCCESS(f'Daily notifications result: {result}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending daily notifications: {str(e)}')
            )
        
        # Check if today is Tuesday to send weekly report
        if datetime.now().weekday() == 1:  # Tuesday is 1
            self.stdout.write('Today is Tuesday, sending weekly report...')
            try:
                result = send_weekly_employees_report()
                self.stdout.write(
                    self.style.SUCCESS(f'Weekly report result: {result}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error sending weekly report: {str(e)}')
                )

        if datetime.now().day == 1:
            self.stdout.write('Today is the first day of the month, sending monthly department-wise probation reports...')
            try:
                result = send_monthly_probation_reports_task()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Monthly department-wise probation report result: {result}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error sending monthly probation reports: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Automatic email notifications completed successfully')
        )