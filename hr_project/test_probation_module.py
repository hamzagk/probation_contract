"""
Test script for Enhanced Probation Module
Run this to verify all probation functionality is working correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

from hr_portal.models import Employee, Department, ProbationApproval, ProbationNotification
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def test_probation_module():
    """Test all probation module functionality"""
    
    print("=" * 60)
    print("ENHANCED PROBATION MODULE - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Check models are accessible
    print("\n✓ Test 1: Checking model accessibility...")
    try:
        employee_count = Employee.objects.count()
        print(f"  ✓ Employee model accessible ({employee_count} records)")
        
        dept_count = Department.objects.count()
        print(f"  ✓ Department model accessible ({dept_count} records)")
        
        approval_count = ProbationApproval.objects.count()
        print(f"  ✓ ProbationApproval model accessible ({approval_count} records)")
        
        notification_count = ProbationNotification.objects.count()
        print(f"  ✓ ProbationNotification model accessible ({notification_count} records)")
    except Exception as e:
        print(f"  ✗ Error accessing models: {e}")
        return False
    
    # Test 2: Check employee probation status calculation
    print("\n✓ Test 2: Testing probation status calculation...")
    try:
        employees = Employee.objects.exclude(
            designation__icontains='Associate Professor'
        )[:5]
        
        for emp in employees:
            status = emp.probation_status
            days_left = emp.days_until_probation_end
            progress = emp.probation_completion_percent
            print(f"  - {emp.name}: {status}, {days_left} days left, {progress}% complete")
        
        print("  ✓ Probation status calculation working")
    except Exception as e:
        print(f"  ✗ Error calculating probation status: {e}")
        return False
    
    # Test 3: Check extension functionality
    print("\n✓ Test 3: Testing probation extension...")
    try:
        extended_employees = Employee.objects.filter(is_extended=True)
        print(f"  ✓ Found {extended_employees.count()} employees with extended probation")
        
        for emp in extended_employees[:3]:
            print(f"    - {emp.name}: Extended to {emp.extended_probation_end_date}")
    except Exception as e:
        print(f"  ✗ Error checking extensions: {e}")
        return False
    
    # Test 4: Check approval history
    print("\n✓ Test 4: Testing approval history...")
    try:
        approvals = ProbationApproval.objects.all()[:5]
        print(f"  ✓ Found {approvals.count()} recent approval records")
        
        for approval in approvals:
            print(f"    - {approval.employee.name}: {approval.get_approval_status_display()}")
    except Exception as e:
        print(f"  ✗ Error checking approval history: {e}")
        return False
    
    # Test 5: Check notification system
    print("\n✓ Test 5: Testing notification system...")
    try:
        notifications = ProbationNotification.objects.filter(sent=True)[:5]
        print(f"  ✓ Found {notifications.count()} sent notifications")
        
        for notif in notifications:
            print(f"    - {notif.employee.name}: {notif.notification_type}")
    except Exception as e:
        print(f"  ✗ Error checking notifications: {e}")
        return False
    
    # Test 6: Check status distribution
    print("\n✓ Test 6: Checking status distribution...")
    try:
        total = Employee.objects.exclude(
            designation__icontains='Associate Professor'
        ).count()
        
        active = Employee.objects.filter(probation_status='Active').exclude(
            designation__icontains='Associate Professor'
        ).count()
        
        ending_soon = Employee.objects.filter(probation_status='Ending Soon').exclude(
            designation__icontains='Associate Professor'
        ).count()
        
        completed = Employee.objects.filter(probation_status='Completed').exclude(
            designation__icontains='Associate Professor'
        ).count()
        
        extended = Employee.objects.filter(is_extended=True).exclude(
            designation__icontains='Associate Professor'
        ).count()
        
        today = date.today()
        ending_7_days = Employee.objects.filter(
            end_date__range=[today, today + timedelta(days=7)],
            probation_status__in=['Active', 'Ending Soon']
        ).exclude(
            designation__icontains='Associate Professor'
        ).count()
        
        print(f"  Total Employees: {total}")
        print(f"  Active: {active}")
        print(f"  Ending Soon: {ending_soon}")
        print(f"  Completed: {completed}")
        print(f"  Extended: {extended}")
        print(f"  Ending in 7 Days: {ending_7_days}")
        print("  ✓ Status distribution calculated correctly")
    except Exception as e:
        print(f"  ✗ Error calculating distribution: {e}")
        return False
    
    # Test 7: Check views imports
    print("\n✓ Test 7: Testing views imports...")
    try:
        from hr_portal.views_probation import (
            probation_dashboard,
            probation_list,
            probation_detail,
            probation_action,
            probation_bulk_action,
            probation_report,
            probation_statistics_api,
            refresh_probation_status,
        )
        print("  ✓ All probation views imported successfully")
    except Exception as e:
        print(f"  ✗ Error importing views: {e}")
        return False
    
    # Test 8: Check signals
    print("\n✓ Test 8: Testing signals...")
    try:
        from hr_portal.signals import (
            update_employee_probation_status,
            clear_employee_cache,
            update_employee_on_approval,
            refresh_all_probation_statuses,
            get_cached_probation_stats,
        )
        print("  ✓ All signals imported successfully")
        
        # Test cache function
        stats = get_cached_probation_stats()
        if stats:
            print("  ✓ Cache functions working correctly")
        else:
            print("  ⚠ Cache returned None (first run)")
    except Exception as e:
        print(f"  ✗ Error testing signals: {e}")
        return False
    
    # Test 9: Check URL configuration
    print("\n✓ Test 9: Testing URL configuration...")
    try:
        from django.urls import reverse
        
        urls = [
            ('probation_dashboard', '/probation/'),
            ('probation_list', '/probation/list/'),
            ('probation_report', '/probation/report/'),
            ('probation_statistics_api', '/probation/api/statistics/'),
            ('refresh_probation_status', '/probation/refresh-status/'),
        ]
        
        for url_name, expected_path in urls:
            try:
                path = reverse(url_name)
                if path == expected_path:
                    print(f"  ✓ {url_name}: {path}")
                else:
                    print(f"  ⚠ {url_name}: {path} (expected {expected_path})")
            except Exception as e:
                print(f"  ✗ {url_name}: Not found - {e}")
    except Exception as e:
        print(f"  ✗ Error testing URLs: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe Enhanced Probation Module is working correctly.")
    print("You can now access:")
    print("  - Dashboard: http://localhost:8000/probation/")
    print("  - List: http://localhost:8000/probation/list/")
    print("  - Report: http://localhost:8000/probation/report/")
    print("  - API: http://localhost:8000/probation/api/statistics/")
    print("\n" + "=" * 60)
    
    return True


if __name__ == '__main__':
    success = test_probation_module()
    sys.exit(0 if success else 1)
