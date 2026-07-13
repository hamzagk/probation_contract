from django.core.management.base import BaseCommand
from hr_portal.models import Department

class Command(BaseCommand):
    help = 'Update department emails to use the correct email address'

    def handle(self, *args, **options):
        # Update all departments to use the correct email
        departments = Department.objects.all()
        updated_count = 0
        
        for dept in departments:
            dept.email = 'muhammad.hamza@giki.edu.pk'
            dept.save()
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Updated department: {dept.name} with email: {dept.email}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Update complete. {updated_count} departments updated.')
        )