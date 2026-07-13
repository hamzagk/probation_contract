import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee

def check_employee_data():
    print("=== Employee Data Check ===")
    
    # Count total employees
    total_employees = Employee.objects.count()
    print(f"Total employees in database: {total_employees}")
    
    if total_employees > 0:
        # Get breakdown by probation status
        from collections import Counter
        statuses = [emp.probation_status for emp in Employee.objects.all()]
        status_counts = Counter(statuses)
        
        print("\nBreakdown by probation status:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        print(f"\nFirst 10 employees:")
        for i, emp in enumerate(Employee.objects.all()[:10]):
            print(f"  {i+1}. {emp.name} (ID: {emp.employee_id}) - {emp.probation_status} - {emp.start_date} to {emp.end_date}")
    
    else:
        print("No employees found in the database.")
    
    print("\n=== End Data Check ===")

if __name__ == "__main__":
    check_employee_data()