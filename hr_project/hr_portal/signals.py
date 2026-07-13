"""
Django signals for automatic probation status updates
Ensures data is always up-to-date without server restarts
"""

from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from hr_portal.models import Employee, ProbationApproval, ProbationNotification
from django.core.cache import cache
from datetime import date
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Employee)
def update_employee_probation_status(sender, instance, **kwargs):
    """
    Automatically update probation status before saving employee
    This ensures status is always current without manual intervention
    """
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    # Skip if this is an update (not creation)
    if instance.pk:
        return
    
    # Automatically calculate end date as 6 months from start date
    instance.end_date = instance.start_date + relativedelta(months=6)
    
    # Associate Professors don't have probation
    if 'Associate Professor' in instance.designation:
        instance.probation_status = 'Completed'
        return
    
    # Use extended end date if probation has been extended
    current_end_date = instance.extended_probation_end_date if instance.is_extended else instance.end_date
    
    # Update probation status based on current date
    if current_end_date < date.today():
        instance.probation_status = 'Completed'
    elif (current_end_date - date.today()).days <= 30 and (current_end_date - date.today()).days >= 0:
        instance.probation_status = 'Ending Soon'
    else:
        instance.probation_status = 'Active'


@receiver(post_save, sender=Employee)
def clear_employee_cache(sender, instance, **kwargs):
    """
    Clear cache when employee is saved to ensure fresh data
    """
    # Clear any cached employee data
    cache.delete(f'employee_{instance.id}_probation_status')
    cache.delete('probation_dashboard_stats')
    cache.delete('probation_list_cache')
    
    logger.info(f"Cache cleared for employee {instance.name} ({instance.employee_id})")


@receiver(post_save, sender=ProbationApproval)
def update_employee_on_approval(sender, instance, **kwargs):
    """
    Update employee status when probation approval is created/updated
    """
    try:
        employee = instance.employee
        
        # Update employee status based on approval
        status_mapping = {
            'approved': 'Completed',
            'rejected': 'Rejected',
            'extended': 'Extended',
            'pending': 'Active'
        }
        
        new_status = status_mapping.get(instance.approval_status, 'Active')
        
        # Only update if status is different
        if employee.probation_status != new_status:
            employee.probation_status = new_status
            
            # If extended, update the end date
            if instance.approval_status == 'extended' and instance.extended_end_date:
                employee.end_date = instance.extended_end_date
                employee.is_extended = True
            
            employee.save(update_fields=['probation_status', 'end_date', 'is_extended'])
            
            logger.info(
                f"Employee {employee.name} status updated to {new_status} "
                f"based on approval {instance.id}"
            )
    except Exception as e:
        logger.error(f"Error updating employee on approval: {str(e)}")


@receiver(post_save, sender=ProbationNotification)
def clear_notification_cache(sender, instance, **kwargs):
    """
    Clear cache when notification is created
    """
    cache.delete(f'employee_{instance.employee_id}_notifications')
    cache.delete('probation_notifications_cache')


def refresh_all_probation_statuses():
    """
    Utility function to refresh all employee probation statuses
    Can be called periodically or on-demand
    """
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    updated_count = 0
    employees = Employee.objects.exclude(
        designation__icontains='Associate Professor'
    )
    
    for employee in employees:
        old_status = employee.probation_status
        
        # Recalculate end date if not extended
        if not employee.is_extended:
            employee.end_date = employee.start_date + relativedelta(months=6)
        
        # Use extended end date if applicable
        current_end_date = employee.extended_probation_end_date if employee.is_extended else employee.end_date
        
        # Recalculate status
        if current_end_date < date.today():
            new_status = 'Completed'
        elif (current_end_date - date.today()).days <= 30 and (current_end_date - date.today()).days >= 0:
            new_status = 'Ending Soon'
        else:
            new_status = 'Active'
        
        # Update if changed
        if old_status != new_status:
            employee.probation_status = new_status
            employee.save(update_fields=['probation_status', 'end_date'])
            updated_count += 1
    
    # Clear all probation-related caches
    cache.clear()
    
    logger.info(f"Refreshed probation statuses: {updated_count} employees updated")
    return updated_count


def get_cached_probation_stats():
    """
    Get probation statistics from cache or calculate if not cached
    Improves performance without requiring server restarts
    """
    cache_key = 'probation_dashboard_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        from datetime import timedelta
        from django.db.models import Count, Q
        
        today = date.today()
        employees = Employee.objects.exclude(
            designation__icontains='Associate Professor'
        )
        
        stats = {
            'total': employees.count(),
            'active': employees.filter(probation_status='Active').count(),
            'ending_soon': employees.filter(probation_status='Ending Soon').count(),
            'completed': employees.filter(probation_status='Completed').count(),
            'extended': employees.filter(is_extended=True).count(),
            'ending_in_7_days': employees.filter(
                end_date__range=[today, today + timedelta(days=7)],
                probation_status__in=['Active', 'Ending Soon']
            ).count(),
            'ending_in_15_days': employees.filter(
                end_date__range=[today, today + timedelta(days=15)],
                probation_status__in=['Active', 'Ending Soon']
            ).count(),
            'ending_in_30_days': employees.filter(
                end_date__range=[today, today + timedelta(days=30)],
                probation_status__in=['Active', 'Ending Soon']
            ).count(),
            'overdue': employees.filter(
                end_date__lt=today,
                probation_status__in=['Active', 'Ending Soon']
            ).count(),
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, stats, 300)
    
    return stats
