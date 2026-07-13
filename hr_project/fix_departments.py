import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Department

def fix_emails():
    departments = Department.objects.filter(email='default@example.com')
    print(f"Found {departments.count()} departments with default@example.com")
    
    for dept in departments:
        print(f"Updating {dept.name} from {dept.email} to muhammad.hamza@giki.edu.pk")
        dept.email = 'muhammad.hamza@giki.edu.pk'
        dept.save()
    print("Done.")

if __name__ == "__main__":
    fix_emails()
