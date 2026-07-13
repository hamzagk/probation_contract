import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def check_specific_employee():
    print("=== Checking Employee ID 200 ===")
    
    # Get all employees and check for ID 200
    all_employees = Employee.objects.all()
    print(f"Total employees: {all_employees.count()}")
    
    for emp in all_employees:
        emp_id = str(emp.employee_id).strip()
        if emp_id in ['200', '200.0']:
            print(f"Found employee with ID '{emp_id}': {emp.name}")
            return
    
    print("Employee with ID 200 or 200.0 not found")
    
    # Let's also check for any employee with ID containing '200'
    print("\nChecking for any employee IDs containing '200':")
    for emp in all_employees:
        emp_id = str(emp.employee_id)
        if '200' in emp_id:
            print(f"Found employee with ID '{emp_id}': {emp.name}")

if __name__ == "__main__":
    check_specific_employee()