import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def remove_float_duplicates():
    """
    Remove duplicate employees where one has a float ID and another has an integer ID
    For example: employee with ID "2.0" and employee with ID "2" - keep only one
    """
    print("=== Removing Float/Integer ID Duplicates ===")
    
    # Get all employees
    all_employees = list(Employee.objects.all())
    print(f"Total employees before cleanup: {len(all_employees)}")
    
    # Create a dictionary to track unique employees by normalized employee_id
    unique_employees = {}  # key: normalized_id, value: employee object
    duplicates = []  # list of employees to delete
    
    for emp in all_employees:
        # Normalize the employee ID by converting to int if possible
        try:
            # Convert to float first to handle "2.0" case, then to int
            normalized_id = int(float(emp.employee_id))
        except (ValueError, TypeError):
            # If conversion fails, keep as string
            normalized_id = str(emp.employee_id).strip()
        
        # Check if we've seen this normalized ID before
        if normalized_id in unique_employees:
            # This is a duplicate - add current employee to duplicates list
            print(f"Found duplicate: {emp.name} (ID: {emp.employee_id}) matches {unique_employees[normalized_id].name} (ID: {unique_employees[normalized_id].employee_id})")
            duplicates.append(emp)
        else:
            # This is the first occurrence - keep it
            unique_employees[normalized_id] = emp
    
    print(f"Found {len(duplicates)} duplicate employees to remove")
    
    # Delete duplicates
    if duplicates:
        print("Deleting duplicates...")
        for dup in duplicates:
            print(f"  Deleting: {dup.name} (ID: {dup.employee_id})")
            dup.delete()
    
    # Count remaining employees
    remaining_count = Employee.objects.count()
    print(f"Remaining employees after cleanup: {remaining_count}")
    
    print("\n=== Cleanup Complete ===")

if __name__ == "__main__":
    remove_float_duplicates()