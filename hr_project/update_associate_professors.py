import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def update_associate_professors():
    """
    Update all Associate Professors to have probation_status = 'Completed'
    """
    print("=== Updating Associate Professors ===")
    
    # Get all Associate Professors
    associate_professors = Employee.objects.filter(designation__icontains='Associate Professor')
    
    print(f"Found {associate_professors.count()} Associate Professor(s)")
    
    updated_count = 0
    for emp in associate_professors:
        old_status = emp.probation_status
        emp.probation_status = 'Completed'
        emp.save()
        print(f"  Updated: {emp.name} - {emp.designation} - Status: {old_status} -> Completed")
        updated_count += 1
    
    print(f"\nUpdated {updated_count} Associate Professor(s) to 'Completed' status")
    print("=== Update Complete ===")

if __name__ == "__main__":
    update_associate_professors()
