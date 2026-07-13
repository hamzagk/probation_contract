import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def check_employee_ids():
    print("=== Checking Employee IDs ===")
    
    # Get all employees
    all_employees = Employee.objects.all()
    print(f"Total employees: {all_employees.count()}")
    
    # Get all employee IDs
    all_ids = []
    for emp in all_employees:
        try:
            emp_id = int(float(emp.employee_id))
            all_ids.append(emp_id)
        except (ValueError, TypeError):
            print(f"Invalid ID format for employee {emp.name}: {emp.employee_id}")
    
    if all_ids:
        all_ids.sort()
        print(f"ID range: {min(all_ids)} to {max(all_ids)}")
        print(f"First 10 IDs: {all_ids[:10]}")
        print(f"Last 10 IDs: {all_ids[-10:]}")
        
        # Check if ID 200 exists
        if 200 in all_ids:
            print("ID 200 exists in the database")
        else:
            print("ID 200 does NOT exist in the database")
    else:
        print("No valid employee IDs found")

if __name__ == "__main__":
    check_employee_ids()