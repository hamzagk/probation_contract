import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee
from datetime import date, timedelta

def test_weekly_report():
    """
    Test the weekly probation report functionality
    This simulates what would be sent on Tuesday
    """
    print("=== Testing Weekly Probation Report ===\n")
    
    # Find employees with probation ending within 30 days (exclude Associate Professors)
    future_date = date.today() + timedelta(days=30)
    employees_queryset = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon']
    ).exclude(designation__icontains='Associate Professor').order_by('end_date')
    
    print(f"Date: {date.today().strftime('%B %d, %Y')}")
    print(f"Report Period: Next 30 days (until {future_date.strftime('%B %d, %Y')})")
    print(f"\nEmployees with probation ending soon: {employees_queryset.count()}\n")
    
    if not employees_queryset.exists():
        print("No employees found with probation ending in the next 30 days.")
    else:
        print("-" * 100)
        print(f"{'ID':<10} {'Name':<30} {'Designation':<25} {'Department':<20} {'End Date':<15} {'Days Left':<10}")
        print("-" * 100)
        
        for emp in employees_queryset:
            emp_id = str(emp.employee_id).rstrip('.0') if str(emp.employee_id).endswith('.0') else str(emp.employee_id)
            days_left = emp.days_until_probation_end
            dept = emp.department.name if emp.department else 'N/A'
            print(f"{emp_id:<10} {emp.name:<30} {emp.designation:<25} {dept:<20} {emp.end_date.strftime('%Y-%m-%d'):<15} {days_left:<10}")
        
        print("-" * 100)
    
    # Count Associate Professors (excluded from report)
    associate_professors = Employee.objects.filter(designation__icontains='Associate Professor')
    print(f"\nAssociate Professors (excluded from report): {associate_professors.count()}")
    
    print("\n=== Test Complete ===")
    print("\nRecipients: muhammad.hamza@giki.edu.pk, muhammad.hamza@giki.edu.pk")
    print("Schedule: Every Tuesday at 9:00 AM")

if __name__ == "__main__":
    test_weekly_report()
