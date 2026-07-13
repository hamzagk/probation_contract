from django.core.management.base import BaseCommand
from datetime import date, timedelta
import calendar
from hr_portal.models import Employee

class Command(BaseCommand):
    help = 'Recalculates probation end dates for all employees'

    def handle(self, *args, **options):
        employees = Employee.objects.all()
        recalculated_count = 0

        for employee in employees:
            original_end_date = employee.end_date

            # Recalculate end date as 6 months from start date
            start = employee.start_date
            month = start.month + 6
            year = start.year
            day = start.day

            if month > 12:
                year += 1
                month -= 12

            # Handle case where the day doesn't exist in the target month
            max_day = calendar.monthrange(year, month)[1]
            if day > max_day:
                day = max_day

            new_end_date = date(year, month, day)

            if original_end_date != new_end_date:
                employee.end_date = new_end_date
                employee.save()
                recalculated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully recalculated probation dates for {recalculated_count} employees')
        )