from django.apps import AppConfig

class HrPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_portal'

    def ready(self):
        # Connect signals
        import hr_portal.signals
        
        import os
        if os.environ.get('RUN_MAIN') != 'true':  # Prevents running during migrations
            try:
                import json
                from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask

                # Create interval schedule for daily checks
                schedule, created = IntervalSchedule.objects.get_or_create(
                    every=1,
                    period=IntervalSchedule.DAYS,
                )

                # Create periodic task for sending notifications
                PeriodicTask.objects.get_or_create(
                    interval=schedule,
                    name='Daily Probation Notifications Check',
                    task='hr_portal.tasks.check_probation_expirations',
                )

                monthly_schedule, created = CrontabSchedule.objects.get_or_create(
                    minute='0',
                    hour='9',
                    day_of_month='1',
                    month_of_year='*',
                    day_of_week='*',
                )

                PeriodicTask.objects.get_or_create(
                    crontab=monthly_schedule,
                    name='Monthly Department Probation Reports',
                    task='hr_portal.tasks.send_monthly_probation_reports_task',
                    defaults={'kwargs': json.dumps({})},
                )
            except RuntimeError:
                # Handle the case where the app isn't fully loaded yet
                pass
            except LookupError:
                # Handle the case where the database tables don't exist yet
                pass