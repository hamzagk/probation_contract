import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def remove_duplicates():
    """
    Remove duplicate employees, keeping only the original Excel sheet records
    """
    print("=== Removing Duplicate Employees ===")
    
    # Get all employees
    all_employees = list(Employee.objects.all())
    print(f"Total employees before cleanup: {len(all_employees)}")
    
    # Create a dictionary to track unique employees by employee_id
    unique_employees = {}
    duplicates = []
    
    for emp in all_employees:
        emp_id = str(emp.employee_id).strip()
        
        if emp_id in unique_employees:
            # This is a duplicate - add to duplicates list
            duplicates.append(emp)
        else:
            # This is the first occurrence - keep it
            unique_employees[emp_id] = emp
    
    print(f"Found {len(duplicates)} duplicate employees")
    
    if duplicates:
        print("Deleting duplicates...")
        for dup in duplicates:
            print(f"  Deleting: {dup.name} (ID: {dup.employee_id})")
            dup.delete()
    
    print(f"Remaining employees after cleanup: {len(unique_employees)}")
    
    # Verify the cleanup
    final_count = Employee.objects.count()
    print(f"Final count: {final_count}")
    
    print("\n=== Cleanup Complete ===")

if __name__ == "__main__":
    remove_duplicates()