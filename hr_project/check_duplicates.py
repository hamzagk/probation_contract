import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def check_duplicates():
    """
    Check for duplicate employees based on name and other fields
    """
    print("=== Checking for Duplicate Employees ===")
    
    # Get all employees
    all_employees = list(Employee.objects.all())
    print(f"Total employees: {len(all_employees)}")
    
    # Check for duplicates based on name
    name_counts = {}
    for emp in all_employees:
        name = emp.name.strip().lower()
        if name in name_counts:
            name_counts[name].append(emp)
        else:
            name_counts[name] = [emp]
    
    # Find names that appear more than once
    duplicates = {name: emps for name, emps in name_counts.items() if len(emps) > 1}
    
    if duplicates:
        print(f"Found {len(duplicates)} names with multiple entries:")
        for name, emps in duplicates.items():
            print(f"\nName: {name}")
            for emp in emps:
                print(f"  - ID: {emp.employee_id}, Name: {emp.name}, Start Date: {emp.start_date}, Status: {emp.probation_status}")
    else:
        print("No duplicates found based on name.")
    
    # Check for duplicates based on employee_id (as floats vs integers)
    id_counts = {}
    for emp in all_employees:
        emp_id = str(emp.employee_id).strip()
        if emp_id in id_counts:
            id_counts[emp_id].append(emp)
        else:
            id_counts[emp_id] = [emp]
    
    # Find IDs that appear more than once
    id_duplicates = {emp_id: emps for emp_id, emps in id_counts.items() if len(emps) > 1}
    
    if id_duplicates:
        print(f"\nFound {len(id_duplicates)} IDs with multiple entries:")
        for emp_id, emps in id_duplicates.items():
            print(f"\nID: {emp_id}")
            for emp in emps:
                print(f"  - ID: {emp.employee_id}, Name: {emp.name}, Start Date: {emp.start_date}, Status: {emp.probation_status}")
    else:
        print("No duplicates found based on employee ID.")
    
    print("\n=== Check Complete ===")

if __name__ == "__main__":
    check_duplicates()