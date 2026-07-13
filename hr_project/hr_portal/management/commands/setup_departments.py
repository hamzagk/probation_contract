from django.core.management.base import BaseCommand
from hr_portal.models import Department

class Command(BaseCommand):
    help = 'Set up default departments with email addresses'

    def handle(self, *args, **options):
        default_departments = [
            {'name': 'Computer Science', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Computer Science Department'},
            {'name': 'Electrical Engineering', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Electrical Engineering Department'},
            {'name': 'Mechanical Engineering', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Mechanical Engineering Department'},
            {'name': 'Mathematics', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Mathematics Department'},
            {'name': 'Physics', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Physics Department'},
            {'name': 'Chemistry', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Chemistry Department'},
            {'name': 'Biology', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Biology Department'},
            {'name': 'Business Administration', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Business Administration Department'},
            {'name': 'Humanities', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'Humanities Department'},
            {'name': 'Other', 'email': 'muhammad.hamza@giki.edu.pk', 'description': 'General Department'},
        ]

        created_count = 0
        for dept_data in default_departments:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'email': dept_data['email'],
                    'description': dept_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created department: {dept.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Department already exists: {dept.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Setup complete. {created_count} departments created.')
        )