"""
Enhanced Probation Management Views
Improved views for better probation management with offline support
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import date, timedelta, datetime
from hr_portal.models import Employee, ProbationApproval, ProbationNotification, Department
from hr_portal.monthly_probation_reports import build_monthly_department_reports, send_monthly_probation_reports
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


def _probation_queryset():
    return Employee.objects.filter(is_contract_record=False).exclude(
        designation__icontains='Associate Professor'
    ).select_related('department')


@login_required
def probation_dashboard(request):
    """
    Enhanced probation dashboard with comprehensive statistics and filtering
    Works offline - no server restart needed
    """
    # Get all employees except Associate Professors for probation stats
    employees_with_probation = _probation_queryset()
    
    # Comprehensive statistics
    total_employees = employees_with_probation.count()
    active_count = employees_with_probation.filter(probation_status='Active').count()
    ending_soon_count = employees_with_probation.filter(probation_status='Ending Soon').count()
    completed_count = employees_with_probation.filter(probation_status='Completed').count()
    extended_count = employees_with_probation.filter(is_extended=True).count()
    
    # Employees by time remaining
    today = date.today()

    ending_in_20_days = employees_with_probation.filter(
        end_date__range=[today, today + timedelta(days=20)],
        probation_status__in=['Active', 'Ending Soon']
    ).count()

    # Recalculate correctly to avoid redundant queries
    stats_base = employees_with_probation.filter(probation_status__in=['Active', 'Ending Soon'])
    ending_in_7_days = stats_base.filter(end_date__range=[today, today + timedelta(days=7)]).count()
    ending_in_20_days = stats_base.filter(end_date__range=[today, today + timedelta(days=20)]).count()
    ending_in_30_days = stats_base.filter(end_date__range=[today, today + timedelta(days=30)]).count()
    
    overdue = employees_with_probation.filter(
        end_date__lt=today,
        probation_status__in=['Active', 'Ending Soon']
    ).count()
    
    # Department-wise breakdown
    dept_stats = employees_with_probation.values(
        'department__name'
    ).annotate(
        total=Count('id'),
        active=Count('id', filter=Q(probation_status='Active')),
        ending_soon=Count('id', filter=Q(probation_status='Ending Soon')),
        completed=Count('id', filter=Q(probation_status='Completed'))
    ).order_by('-total')
    
    # Recent probation completions (last 7 days)
    recent_completions = employees_with_probation.filter(
        probation_status='Completed',
        end_date__range=[today - timedelta(days=7), today]
    ).order_by('-end_date')[:10]
    
    # Upcoming expirations (next 30 days)
    upcoming_expirations = employees_with_probation.filter(
        end_date__range=[today, today + timedelta(days=30)],
        probation_status__in=['Active', 'Ending Soon']
    ).order_by('end_date')[:15]
    
    # Pending approvals
    pending_approvals = ProbationApproval.objects.filter(
        approval_status='pending'
    ).select_related('employee').order_by('-created_at')[:10]

    monthly_reports = build_monthly_department_reports(today)
    monthly_report_departments = len(monthly_reports)
    monthly_report_employees = sum(
        report['employee_count'] for report in monthly_reports
    )
    
    context = {
        'total_employees': total_employees,
        'active_count': active_count,
        'ending_soon_count': ending_soon_count,
        'completed_count': completed_count,
        'extended_count': extended_count,
        'ending_in_7_days': ending_in_7_days,
        'ending_in_20_days': ending_in_20_days,
        'ending_in_30_days': ending_in_30_days,
        'overdue': overdue,
        'dept_stats': dept_stats,
        'recent_completions': recent_completions,
        'upcoming_expirations': upcoming_expirations,
        'pending_approvals': pending_approvals,
        'monthly_report_departments': monthly_report_departments,
        'monthly_report_employees': monthly_report_employees,
        'today': today,
    }
    
    return render(request, 'hr_portal/probation_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def send_monthly_probation_report_manual(request):
    """Send the department-wise monthly probation report manually from the dashboard."""
    try:
        result = send_monthly_probation_reports()
    except Exception as e:
        logger.error(f"Manual monthly probation report error: {str(e)}")
        messages.error(
            request,
            f"Monthly department-wise probation report could not be sent: {str(e)}",
        )
        return redirect('probation_dashboard')

    if result['sent_reports'] == 0 and result['skipped_reports'] == 0:
        messages.warning(
            request,
            f"No employees are scheduled to complete probation in {result['report_month_label']}.",
        )
    elif result['sent_reports'] == 0:
        messages.warning(
            request,
            f"Monthly department-wise probation reports for {result['report_month_label']} "
            f"were already sent. Skipped {result['skipped_reports']} department(s).",
        )
    else:
        messages.success(
            request,
            f"Monthly department-wise probation reports for {result['report_month_label']} sent "
            f"to {result['sent_reports']} department(s). Skipped {result['skipped_reports']}.",
        )

    return redirect('probation_dashboard')


@login_required
def probation_list(request):
    """
    Enhanced probation employee list with advanced filtering
    Works offline - cached queries, no server restart needed
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    department_filter = request.GET.get('department', '')
    search_query = request.GET.get('q', '')
    date_range = request.GET.get('date_range', '')
    extension_filter = request.GET.get('extension', '')
    
    # Base queryset - exclude Associate Professors
    employees = _probation_queryset()
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        if status_filter in ['Active', 'Ending Soon', 'Completed', 'Extended', 'Rejected']:
            employees = employees.filter(probation_status=status_filter)
    
    # Apply department filter
    if department_filter and department_filter != 'all':
        employees = employees.filter(department_id=department_filter)
    
    # Apply extension filter
    if extension_filter:
        if extension_filter == 'extended':
            employees = employees.filter(is_extended=True)
        elif extension_filter == 'not_extended':
            employees = employees.filter(is_extended=False)
    
    # Apply date range filter
    today = date.today()
    if date_range:
        if date_range == 'ending_7':
            employees = employees.filter(
                end_date__range=[today, today + timedelta(days=7)]
            )
        elif date_range == 'ending_20':
            employees = employees.filter(
                end_date__range=[today, today + timedelta(days=20)]
            )
        elif date_range == 'ending_30':
            employees = employees.filter(
                end_date__range=[today, today + timedelta(days=30)]
            )
        elif date_range == 'overdue':
            employees = employees.filter(
                end_date__lt=today,
                probation_status__in=['Active', 'Ending Soon']
            )
        elif date_range == 'completed_week':
            employees = employees.filter(
                probation_status='Completed',
                end_date__range=[today - timedelta(days=7), today]
            )
    
    # Apply search query
    if search_query:
        employees = employees.filter(
            Q(name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
    
    # Order by end_date (most urgent first)
    employees = employees.order_by('end_date')
    
    # Pagination
    paginator = Paginator(employees, 20)  # Show 20 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get departments for filter dropdown
    departments = Department.objects.annotate(
        employee_count=Count('employee')
    ).filter(employee_count__gt=0).order_by('name')
    
    # Prepare statistics for the page
    stats = {
        'total': employees.count(),
        'active': employees.filter(probation_status='Active').count(),
        'ending_soon': employees.filter(probation_status='Ending Soon').count(),
        'completed': employees.filter(probation_status='Completed').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'search_query': search_query,
        'date_range': date_range,
        'extension_filter': extension_filter,
        'departments': departments,
        'stats': stats,
        'today': today,
    }
    
    return render(request, 'hr_portal/probation_list.html', context)


@login_required
@require_http_methods(["POST"])
def probation_bulk_action(request):
    """
    Handle bulk actions on multiple employees
    Actions: approve, extend, reject
    """
    try:
        data = json.loads(request.body)
        employee_ids = data.get('employee_ids', [])
        action = data.get('action', '')
        comments = data.get('comments', '')
        extension_months = data.get('extension_months', 3)
        
        if not employee_ids or not action:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request parameters'
            })
        
        action_map = {
            'approve': 'approved',
            'reject': 'rejected',
            'extend': 'extended'
        }
        
        if action not in action_map:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            })
        
        processed_count = 0
        failed_count = 0
        
        for emp_id in employee_ids:
            try:
                employee = _probation_queryset().get(pk=emp_id)
                
                # Create probation approval record
                approval = ProbationApproval.objects.create(
                    employee=employee,
                    approval_status=action_map[action],
                    requested_by=request.user.username,
                    comments=comments,
                    extension_months=extension_months if action == 'extend' else 0
                )
                
                # Handle extension
                if action == 'extend':
                    from dateutil.relativedelta import relativedelta
                    current_end_date = employee.end_date
                    new_end_date = current_end_date + relativedelta(months=extension_months)
                    
                    employee.extended_probation_end_date = new_end_date
                    employee.is_extended = True
                    approval.extended_end_date = new_end_date
                    approval.save()
                
                # Update employee probation status
                if action == 'approve':
                    employee.probation_status = 'Completed'
                elif action == 'reject':
                    employee.probation_status = 'Rejected'
                elif action == 'extend':
                    employee.probation_status = 'Extended'
                    employee.end_date = new_end_date
                
                employee.save()
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing employee {emp_id}: {str(e)}")
                failed_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully processed {processed_count} employees. {failed_count} failed.',
            'processed_count': processed_count,
            'failed_count': failed_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        })
    except Exception as e:
        logger.error(f"Bulk action error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def probation_action(request, employee_id):
    """
    Handle individual probation actions (approve, extend, reject)
    Works offline - immediate update without server restart
    """
    try:
        employee = get_object_or_404(_probation_queryset(), pk=employee_id)
        data = json.loads(request.body)
        
        action = data.get('action', '').lower()
        comments = data.get('comments', '')
        extension_months = data.get('extension_months', 3)
        
        action_map = {
            'approve': 'approved',
            'reject': 'rejected',
            'extend': 'extended'
        }
        
        if action not in action_map:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            })
        
        # Create probation approval record
        approval = ProbationApproval.objects.create(
            employee=employee,
            approval_status=action_map[action],
            requested_by=request.user.username,
            comments=comments,
            extension_months=extension_months if action == 'extend' else 0
        )
        
        # Handle extension
        if action == 'extend':
            from dateutil.relativedelta import relativedelta
            current_end_date = employee.end_date
            new_end_date = current_end_date + relativedelta(months=extension_months)
            
            employee.extended_probation_end_date = new_end_date
            employee.is_extended = True
            approval.extended_end_date = new_end_date
            approval.save()
        
        # Update employee probation status
        if action == 'approve':
            employee.probation_status = 'Completed'
        elif action == 'reject':
            employee.probation_status = 'Rejected'
        elif action == 'extend':
            employee.probation_status = 'Extended'
            employee.end_date = new_end_date
        
        employee.save()
        
        # Send notification email if configured
        send_probation_action_email(employee, action, comments, approval)
        
        return JsonResponse({
            'success': True,
            'message': f'Probation {action}ed successfully for {employee.name}',
            'employee_id': employee.id,
            'new_status': employee.probation_status,
            'approval_id': approval.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        })
    except Exception as e:
        logger.error(f"Probation action error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


def send_probation_action_email(employee, action, comments, approval):
    """Send email notification for probation action"""
    try:
        # Determine recipient
        recipient_email = employee.department.email if employee.department and employee.department.email else None
        if not recipient_email:
            recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
        
        # CC list
        hr_cc_emails = getattr(settings, 'HR_EMAIL_LIST', [
            'muhammad.hamza@giki.edu.pk',
            'muhammad.hamza@giki.edu.pk',
            'nasirali@giki.edu.pk'
        ])
        
        # Subject based on action
        action_labels = {
            'approve': 'Probation Completed',
            'reject': 'Probation Rejected',
            'extend': 'Probation Extended'
        }
        
        subject = f"{action_labels.get(action, 'Probation Update')} - {employee.name} ({employee.employee_id})"
        
        # Render email template
        context = {
            'employee': employee,
            'action': action,
            'action_label': action_labels.get(action, 'Probation Update'),
            'comments': comments,
            'approval': approval,
            'current_date': date.today().strftime('%B %d, %Y')
        }
        
        html_message = render_to_string(
            'hr_portal/probation_action_email.html',
            context
        )
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Probation {action} notification for {employee.name}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
            cc=hr_cc_emails
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
    except Exception as e:
        logger.error(f"Error sending probation action email: {str(e)}")


@login_required
def probation_detail(request, employee_id):
    """
    Detailed view of employee probation status
    Works offline - uses cached data
    """
    employee = get_object_or_404(_probation_queryset(), pk=employee_id)
    
    # Get approval history
    approval_history = ProbationApproval.objects.filter(
        employee=employee
    ).order_by('-created_at')
    
    # Calculate statistics
    total_probation_days = 180
    days_completed = total_probation_days - employee.days_until_probation_end
    progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0
    
    # Get notification history
    notifications = ProbationNotification.objects.filter(
        employee=employee
    ).order_by('-notification_date')[:10]
    
    context = {
        'employee': employee,
        'approval_history': approval_history,
        'progress_percentage': progress_percentage,
        'notifications': notifications,
        'today': date.today()
    }
    
    return render(request, 'hr_portal/probation_detail.html', context)


@login_required
def probation_report(request):
    """
    Generate comprehensive probation report
    Works offline - generates on-demand without server restart
    """
    # Get report parameters
    report_type = request.GET.get('type', 'summary')
    department_id = request.GET.get('department', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    employees = _probation_queryset()
    
    # Apply filters
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            employees = employees.filter(start_date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            employees = employees.filter(end_date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Generate report data
    today = date.today()
    
    if report_type == 'summary':
        report_data = {
            'title': 'Probation Summary Report',
            'generated_at': timezone.now(),
            'total_employees': employees.count(),
            'by_status': {
                'active': employees.filter(probation_status='Active').count(),
                'ending_soon': employees.filter(probation_status='Ending Soon').count(),
                'completed': employees.filter(probation_status='Completed').count(),
                'extended': employees.filter(is_extended=True).count(),
            },
            'by_timeframe': {
                'ending_7_days': employees.filter(
                    end_date__range=[today, today + timedelta(days=7)],
                    probation_status__in=['Active', 'Ending Soon']
                ).count(),
                'ending_15_days': employees.filter(
                    end_date__range=[today, today + timedelta(days=15)],
                    probation_status__in=['Active', 'Ending Soon']
                ).count(),
                'ending_30_days': employees.filter(
                    end_date__range=[today, today + timedelta(days=30)],
                    probation_status__in=['Active', 'Ending Soon']
                ).count(),
                'overdue': employees.filter(
                    end_date__lt=today,
                    probation_status__in=['Active', 'Ending Soon']
                ).count(),
            }
        }
    
    elif report_type == 'detailed':
        report_data = {
            'title': 'Detailed Probation Report',
            'generated_at': timezone.now(),
            'employees': []
        }
        
        for emp in employees:
            report_data['employees'].append({
                'employee_id': emp.employee_id,
                'name': emp.name,
                'designation': emp.designation,
                'department': emp.department.name if emp.department else 'N/A',
                'start_date': emp.start_date,
                'end_date': emp.end_date,
                'probation_status': emp.probation_status,
                'is_extended': emp.is_extended,
                'days_remaining': emp.days_until_probation_end,
                'completion_percent': emp.probation_completion_percent
            })
    
    elif report_type == 'ending_soon':
        report_data = {
            'title': 'Probation Ending Soon Report',
            'generated_at': timezone.now(),
            'employees': employees.filter(
                end_date__range=[today, today + timedelta(days=30)],
                probation_status__in=['Active', 'Ending Soon']
            ).order_by('end_date')
        }
    
    # Get departments for filter
    departments = Department.objects.annotate(
        employee_count=Count('employee', filter=Q(employee__is_contract_record=False))
    ).filter(employee_count__gt=0).order_by('name')
    
    context = {
        'report_data': report_data,
        'report_type': report_type,
        'departments': departments,
        'selected_department': department_id,
        'date_from': date_from,
        'date_to': date_to,
        'today': today
    }
    
    return render(request, 'hr_portal/probation_report.html', context)


@login_required
def probation_statistics_api(request):
    """
    API endpoint for probation statistics
    Used for real-time updates without server restart
    """
    today = date.today()
    employees = _probation_queryset()
    
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
        'ending_in_20_days': employees.filter(
            end_date__range=[today, today + timedelta(days=20)],
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
    
    # Department breakdown
    dept_stats = list(employees.values(
        'department__name'
    ).annotate(
        total=Count('id'),
        active=Count('id', filter=Q(probation_status='Active')),
        ending_soon=Count('id', filter=Q(probation_status='Ending Soon')),
        completed=Count('id', filter=Q(probation_status='Completed'))
    ).order_by('-total')[:10])
    
    return JsonResponse({
        'success': True,
        'statistics': stats,
        'department_stats': dept_stats,
        'generated_at': timezone.now().isoformat()
    })


@login_required
def refresh_probation_status(request):
    """
    Manual refresh endpoint to recalculate all probation statuses
    Ensures data is up-to-date without server restart
    """
    try:
        updated_count = 0
        employees = _probation_queryset()
        
        for employee in employees:
            old_status = employee.probation_status
            # Force save to recalculate status
            employee.save()
            
            if old_status != employee.probation_status:
                updated_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Probation statuses refreshed. {updated_count} employees updated.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error refreshing statuses: {str(e)}'
        })
