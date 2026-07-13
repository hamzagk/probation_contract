import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def remove_name_duplicates():
    """
    Remove duplicate employees based on name, keeping the one with lower employee_id
    """
    print("=== Removing Duplicate Employees by Name ===")

    # Get all employees
    all_employees = list(Employee.objects.all())
    print(f"Total employees before cleanup: {len(all_employees)}")

    # Create a dictionary to track employees by name (case-insensitive)
    name_groups = {}
    for emp in all_employees:
        name = emp.name.strip().lower()
        if name in name_groups:
            name_groups[name].append(emp)
        else:
            name_groups[name] = [emp]

    # Find names that appear more than once
    duplicates = {name: emps for name, emps in name_groups.items() if len(emps) > 1}

    if not duplicates:
        print("No duplicates found based on name.")
        return

    print(f"Found {len(duplicates)} names with multiple entries:")
    
    deleted_count = 0
    for name, emps in duplicates.items():
        print(f"\nName: {name}")
        
        # Sort by employee_id (as float) to keep the first one
        emps_sorted = sorted(emps, key=lambda x: float(x.employee_id))
        
        # Keep the first one (lowest ID), delete the rest
        keep = emps_sorted[0]
        to_delete = emps_sorted[1:]
        
        print(f"  Keeping: ID: {keep.employee_id}, Name: {keep.name}, Start Date: {keep.start_date}")
        
        for emp in to_delete:
            print(f"  Deleting: ID: {emp.employee_id}, Name: {emp.name}, Start Date: {emp.start_date}")
            emp.delete()
            deleted_count += 1

    print(f"\nDeleted {deleted_count} duplicate employees")
    print(f"Remaining employees after cleanup: {Employee.objects.count()}")

    print("\n=== Cleanup Complete ===")

if __name__ == "__main__":
    remove_name_duplicates()
