"""
Views for HR Portal application
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
from hr_portal.models import (
    Department,
    DocumentTemplate,
    Employee,
    EmployeeDocument,
    GeneratedDocument,
    ProbationApproval,
    ProbationNotification,
)
from hr_portal.forms import EmployeeForm, EmployeeUploadForm
from hr_portal.monthly_probation_reports import build_monthly_department_reports
from hr_portal.utils import generate_document_template
import os
import json
import logging

logger = logging.getLogger(__name__)

def get_employee_by_id(employee_id):
    """Helper to find employee by employee_id (S.#) field, handling float/string variations"""
    eid_str = str(employee_id)
    if eid_str.endswith('.0'):
        eid_str = eid_str[:-2]
    
    possible_ids = [eid_str, f"{eid_str}.0"]
    for eid in possible_ids:
        try:
            return Employee.objects.get(employee_id=eid)
        except Employee.DoesNotExist:
            continue
    return None

@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get counts for dashboard statistics
    total_employees = Employee.objects.count()
    # Exclude Associate Professors from probation statistics (they don't have probation)
    employees_with_probation = Employee.objects.exclude(designation__icontains='Associate Professor')
    
    # Using probation_status to determine active/inactive employees (excluding Associate Professors)
    active_employees = employees_with_probation.filter(probation_status='Active').count()
    ending_soon_employees = employees_with_probation.filter(probation_status='Ending Soon').count()
    # Include Associate Professors in completed count since they're considered completed
    completed_employees = Employee.objects.filter(probation_status='Completed').count()

    # Get employees with upcoming probation ends (current month or next 30 days) - exclude Associate Professors
    start_of_month = timezone.now().date().replace(day=1)
    future_date = timezone.now().date() + timedelta(days=30)
    
    # Use a list to allow modification of attributes for the template if needed
    upcoming_expirations = list(employees_with_probation.filter(
        end_date__range=[start_of_month, future_date]
    ).order_by('end_date'))
    probation_ending_soon = upcoming_expirations
    
    # Clean up IDs for the template (remove .0)
    for emp in upcoming_expirations:
        if str(emp.employee_id).endswith('.0'):
            emp.display_id = str(emp.employee_id)[:-2]
        else:
            emp.display_id = str(emp.employee_id)

    # Get recently added employees (last 30 days) - using start_date as a proxy for created date
    recent_date = timezone.now().date() - timedelta(days=30)
    recent_employees = Employee.objects.filter(start_date__gte=recent_date).order_by('-start_date')[:5]

    # Prepare data for charts
    from django.db.models import Count
    department_stats = Employee.objects.values('department__name').annotate(count=Count('id')).order_by('-count')
    departments = [item['department__name'] or 'Unassigned' for item in department_stats]
    department_counts = [item['count'] for item in department_stats]

    # Probation status stats (excluding Associate Professors)
    probation_status_stats = employees_with_probation.values('probation_status').annotate(count=Count('id'))
    probation_status_dict = {item['probation_status']: item['count'] for item in probation_status_stats}
    probation_status_counts = [
        probation_status_dict.get('Active', 0),
        probation_status_dict.get('Ending Soon', 0),
        probation_status_dict.get('Completed', 0)
    ]

    monthly_reports = build_monthly_department_reports()
    monthly_report_departments = len(monthly_reports)
    monthly_report_employees = sum(
        report['employee_count'] for report in monthly_reports
    )

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'ending_soon_employees': ending_soon_employees,
        'completed_employees': completed_employees,
        'probation_ending_soon': probation_ending_soon,
        'upcoming_expirations': upcoming_expirations,
        'recent_employees': recent_employees,
        'departments': departments,
        'department_counts': department_counts,
        'probation_status_counts': probation_status_counts,
        'monthly_report_departments': monthly_report_departments,
        'monthly_report_employees': monthly_report_employees,
    }

    return render(request, 'hr_portal/dashboard.html', context)

@login_required
def employee_list(request):
    """List all employees with search and pagination"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')  # Get status filter from URL parameter

    employees = Employee.objects.all()

    # Apply status filter if provided
    if status_filter:
        if status_filter in ['Active', 'Ending Soon', 'Completed']:
            employees = employees.filter(probation_status=status_filter)

    # Apply search query if provided
    if query:
        employees = employees.filter(
            Q(name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(designation__icontains=query) |
            Q(department__name__icontains=query)
        )

    # Order by start_date
    employees = employees.order_by('-start_date')

    # Pagination
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    templates = DocumentTemplate.objects.filter(is_active=True).order_by('name')

    return render(request, 'hr_portal/employee_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'templates': templates,
        'active_count': Employee.objects.filter(probation_status='Active').count(),
        'ending_soon_count': Employee.objects.filter(probation_status='Ending Soon').count(),
        'completed_count': Employee.objects.filter(probation_status='Completed').count(),
    })

@login_required
def add_employee(request):
    """Add a new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.name} added successfully!')
            return redirect('employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()
    
    return render(request, 'hr_portal/add_employee.html', {'form': form})

@login_required
def edit_employee(request, employee_id):
    """Edit an existing employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.name} updated successfully!')
            return redirect('employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'hr_portal/edit_employee.html', {'form': form, 'employee': employee})

@login_required
def delete_employee(request, employee_id):
    """Delete an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        employee.delete()
        messages.success(request, f'Employee {employee.name} deleted successfully!')
        return redirect('employee_list')
    
    return render(request, 'hr_portal/delete_employee.html', {'employee': employee})

@login_required
def upload_document(request, employee_id=None):
    """Upload a document for an employee or general document"""
    employee = None
    if employee_id:
        employee = get_employee_by_id(employee_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        document_type = request.POST.get('document_type', 'other')
        description = request.POST.get('description', '')
        file = request.FILES.get('file')

        if file and title:
            document = EmployeeDocument.objects.create(
                employee=employee,
                title=title,
                document_type=document_type,
                file=file,
                description=description
            )
            messages.success(request, 'Document uploaded successfully!')
            if employee:
                return redirect('employee_documents', employee_id=employee.id)
            else:
                return redirect('documents')
        else:
            messages.error(request, 'Please provide a title and file.')
    else:
        # Prepare empty form context
        pass

    return render(request, 'hr_portal/upload_document.html', {
        'employee': employee
    })

@login_required
def employee_documents(request, employee_id):
    """View documents for a specific employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')

    documents = EmployeeDocument.objects.filter(employee=employee).order_by('-uploaded_at')

    return render(request, 'hr_portal/employee_documents.html', {
        'employee': employee,
        'documents': documents
    })

@login_required
def generate_document(request, employee_id):
    """Generate a document for an employee using AI"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        additional_info = request.POST.get('additional_info', '')

        # In a real implementation, this would call an AI service
        # For now, we'll just simulate document generation
        try:
            # Get employee data
            employee_data = {
                'name': employee.name,
                'employee_id': employee.employee_id,
                'designation': employee.designation,
                'department': employee.department.name if employee.department else 'N/A',
                'start_date': employee.start_date,
                'end_date': employee.end_date if employee.end_date else 'N/A',
            }

            # Create document content based on type
            if document_type == 'service_certificate':
                content = f"SERVICE CERTIFICATE\n\nThis is to certify that {employee.name} with employee ID {employee.employee_id} has served at GIK Institute in the capacity of {employee.designation} in the {employee.department.name if employee.department else 'N/A'} department."
            elif document_type == 'experience_certificate':
                content = f"EXPERIENCE CERTIFICATE\n\nThis is to certify the work experience of {employee.name} with employee ID {employee.employee_id} who worked as {employee.designation} in the {employee.department.name if employee.department else 'N/A'} department at GIK Institute."
            elif document_type == 'relieving_letter':
                content = f"RELIEVING LETTER\n\nThis letter serves as a relieving letter for {employee.name} with employee ID {employee.employee_id} from their position as {employee.designation} in the {employee.department.name if employee.department else 'N/A'} department at GIK Institute."
            else:
                content = f"DOCUMENT\n\nThis is a generated document for {employee.name} with employee ID {employee.employee_id}."

            # For now, we'll save this as a text file
            from django.core.files.base import ContentFile
            import tempfile
            import os

            # Create a temporary file with the content
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name

            # Create an EmployeeDocument object
            from django.core.files import File
            with open(tmp_file_path, 'rb') as f:
                doc = EmployeeDocument.objects.create(
                    employee=employee,
                    title=f"{document_type.replace('_', ' ').title()} - {employee.name}",
                    document_type='other',
                    description=f"AI-generated {document_type.replace('_', ' ')} for {employee.name}",
                )
                doc.file.save(f"{document_type}_{employee.employee_id}.txt", File(f))

            # Clean up the temporary file
            os.unlink(tmp_file_path)

            messages.success(request, f'{document_type.replace("_", " ").title()} generated and saved successfully!')
            return redirect('employee_documents', employee_id=employee.id)

        except Exception as e:
            messages.error(request, f'Error generating document: {str(e)}')

    return render(request, 'hr_portal/generate_document.html', {'employee': employee})

@login_required
def documents(request):
    """View all documents"""
    documents = EmployeeDocument.objects.all().order_by('-uploaded_at')
    return render(request, 'hr_portal/documents.html', {'documents': documents})

def create_document_prompt(document_type, employee_data, additional_info):
    """Create a prompt for document generation based on type and employee data"""
    # This function was causing syntax errors, so I'm providing a clean implementation
    employee_info = f"""
    Employee Information:
    - Name: {employee_data.get('name', 'N/A')}
    - Employee ID: {employee_data.get('employee_id', 'N/A')}
    - Designation: {employee_data.get('designation', 'N/A')}
    - Department: {employee_data.get('department', 'N/A')}
    - Start Date: {employee_data.get('start_date', 'N/A')}
    """

    if document_type == 'service_certificate':
        return f"""
        Generate a formal service certificate for the GIK Institute. Include:
        {employee_info}

        Format the certificate professionally with:
        - GIK Institute letterhead reference
        - Certificate title
        - Formal recognition of service
        - Specific dates of employment
        - Appropriate closing
        - Signature block

        Additional Information: {additional_info}
        """
    elif document_type == 'experience_certificate':
        return f"""
        Generate a formal experience certificate for the GIK Institute. Include:
        {employee_info}

        Format the certificate professionally with:
        - GIK Institute letterhead reference
        - Certificate title
        - Confirmation of employment
        - Job responsibilities summary
        - Duration of service
        - Professional closing
        - Authorized signature
        """
    elif document_type == 'relieving_letter':
        return f"""
        Generate a formal relieving letter for the GIK Institute. Include:
        {employee_info}

        Format the letter professionally with:
        - Letterhead
        - Date
        - Employee name and details
        - Statement of relief from duties
        - Acknowledgment of service
        - Closing remarks
        - Authorized signature
        """
    else:
        return f"""
        Generate the requested document for the GIK Institute. Include:
        {employee_info}
        
        Additional Information: {additional_info}
        """

# Additional view for sending employee lists to HR (fixed version)
@login_required
def send_employees_list_to_hrs(request):
    """Send a list of employees whose probation is ending soon to HR members"""
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    from datetime import date, timedelta
    from django.http import JsonResponse
    import json

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              'application/json' in request.headers.get('Accept', '')

    if request.method == 'POST':
        # Find employees with probation ending in the current month or within the next 30 days
        # This ensures we catch everyone from the start of the current month up to one month from today
        start_of_month = date.today().replace(day=1)
        future_date = date.today() + timedelta(days=30)
        
        employees_queryset = Employee.objects.filter(
            end_date__range=[start_of_month, future_date]
        ).exclude(
            designation__icontains='Associate Professor'
        ).order_by('end_date')

        if not employees_queryset.exists():
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'No employees found with ending probation.'})
            messages.info(request, 'No employees found with ending probation.')
            return redirect('employee_list')

        # Prepare employee data with additional computed fields for the template
        employees = []
        for emp in employees_queryset:
            # Calculate probation progress percentage
            total_probation_days = 180  # Assuming 6 months probation (approx.)
            days_completed = total_probation_days - emp.days_until_probation_end
            progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

            # Create a dict with all the properties needed for the template
            # Remove trailing .0 from employee ID if present
            emp_id = str(emp.employee_id)
            if emp_id.endswith('.0'):
                emp_id = emp_id[:-2]

            emp_data = {
                'id': emp_id,  # Fixed to remove trailing .0
                'name': emp.name,
                'designation': emp.designation,
                'department': emp.department,
                'start_date': emp.start_date.strftime('%B %d, %Y'),
                'end_date': emp.end_date.strftime('%B %d, %Y'),
                'days_until_probation_end': emp.days_until_probation_end,
                'probation_completion_percent': emp.probation_completion_percent,
            }
            employees.append(emp_data)

        # Prepare context for the email template
        context = {
            'employees': employees,
            'current_date': date.today().strftime('%B %d, %Y'),
            'report_title': 'Employees with Ending Probation',
            'report_period': f"From {start_of_month.strftime('%B %d')} to {future_date.strftime('%B %d, %Y')}",
            'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
        }

        # Render the HTML email template
        html_message = render_to_string('hr_portal/probation_report_email.html', context)

        # Use the HR email list from settings
        hr_emails = getattr(settings, 'HR_EMAIL_LIST', [
            'muhammad.hamza@giki.edu.pk',
            'nasirali@giki.edu.pk'
        ])

        # Create and send the email to all HR members
        subject = f"Weekly Probation Report: {len(employees)} Employees with Ending Probation ({date.today().strftime('%B %d, %Y')})"

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"This is an HTML email report containing a list of employees whose probation periods are ending soon. Please view it in a compatible email client.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=hr_emails  # Send to all HR members
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            success_message = f'Probation report sent successfully to {len(hr_emails)} HR members. Report contains {len(employees)} employees.'
        except Exception as e:
            error_message = f'Error sending email: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_message})
            
            messages.error(request, error_message)
            return redirect('employee_list')

        if is_ajax:
            return JsonResponse({'success': True, 'message': success_message})

        messages.success(request, success_message)
        return redirect('employee_list')

    # If not POST, redirect to dashboard
    return redirect('dashboard')

@login_required
def employee_create(request):
    """Create a new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.name} created successfully!')
            return redirect('employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()

    return render(request, 'hr_portal/employee_form.html', {'form': form})

@login_required
def import_employees_from_excel(request):
    """Import employees from Excel file"""
    if request.method == 'POST':
        form = EmployeeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'Please upload a valid Excel file (.xlsx or .xls)')
                return render(request, 'hr_portal/import_employees.html', {'form': form})

            try:
                import pandas as pd
                import datetime
                
                # Load the Excel file
                xl = pd.ExcelFile(excel_file)
                
                # Column mapping for flexibility
                column_mapping = {
                    'employee_id': ['employee_id', 'emp_id', 'id', 'employeeid', 'epi #', 's.#'],
                    'name': ['name', 'full_name', 'fullname', 'employee_name'],
                    'designation': ['designation', 'position', 'job_title', 'title', 'role'],
                    'department': ['department', 'dept', 'division', 'function'],
                    'start_date': ['start_date', 'hire_date', 'joining_date', 'date_joined', 'doj'],
                    'contract_start_date': ['contract_start_date', 'contract start date', 'contract_start', 'contract date'],
                    'contract_duration_months': ['contract_duration_months', 'contract duration', 'duration_months', 'contract months']
                }
                
                df = None
                actual_columns = {}
                
                # Try to find a sheet with the required columns
                for sheet_name in xl.sheet_names:
                    temp_df = pd.read_excel(xl, sheet_name=sheet_name)
                    
                    # If the sheet is empty or has very few columns, skip
                    if temp_df.empty or len(temp_df.columns) < 2:
                        continue
                        
                    # Check if this sheet has at least name and employee_id (or similar)
                    found_cols = {}
                    for model_field, possible_names in column_mapping.items():
                        for name in possible_names:
                            matches = [col for col in temp_df.columns if str(col).lower().strip() == name]
                            if matches:
                                found_cols[model_field] = matches[0]
                                break
                    
                    # If we found at least name and start_date, or employee_id, this might be the right sheet
                    if ('name' in found_cols and 'start_date' in found_cols) or \
                       ('employee_id' in found_cols and 'name' in found_cols):
                        df = temp_df
                        actual_columns = found_cols
                        break
                
                if df is None:
                    # If no sheet matches perfectly, try the first sheet but maybe it needs skipping rows
                    first_sheet = xl.sheet_names[0]
                    df = pd.read_excel(xl, sheet_name=first_sheet)
                    
                    # Check if the first row is actually a header (common in some exports)
                    # Look for our keywords in the first 5 rows
                    for skip in range(1, 5):
                        temp_df = pd.read_excel(xl, sheet_name=first_sheet, skiprows=skip)
                        found_cols = {}
                        for model_field, possible_names in column_mapping.items():
                            for name in possible_names:
                                matches = [col for col in temp_df.columns if str(col).lower().strip() == name]
                                if matches:
                                    found_cols[model_field] = matches[0]
                                    break
                        if ('name' in found_cols and 'start_date' in found_cols) or \
                           ('employee_id' in found_cols and 'name' in found_cols):
                            df = temp_df
                            actual_columns = found_cols
                            break

                if not actual_columns or 'name' not in actual_columns:
                    messages.error(request, 'Could not identify required columns (Name, Start Date) in any sheet.')
                    return render(request, 'hr_portal/import_employees.html', {'form': form})

                # Process the Excel data and create employees
                created_count = 0
                for index, row in df.iterrows():
                    try:
                        # Get values from the mapped columns
                        employee_id = str(row[actual_columns['employee_id']]).strip() if 'employee_id' in actual_columns else None
                        # If employee_id is a float like '109.0', convert to '109'
                        if employee_id and employee_id.endswith('.0'):
                            employee_id = employee_id[:-2]
                        
                        # Generate ID if missing
                        if not employee_id or employee_id.lower() == 'nan':
                            continue # Skip rows without ID if possible, or generate one
                            
                        name = str(row[actual_columns['name']]).strip()
                        if not name or name.lower() == 'nan':
                            continue
                            
                        designation = str(row[actual_columns.get('designation', '')]).strip() if 'designation' in actual_columns else "Staff"
                        if designation.lower() == 'nan': designation = "Staff"
                        
                        department_name = str(row[actual_columns.get('department', '')]).strip() if 'department' in actual_columns else "General"
                        if department_name.lower() == 'nan': department_name = "General"
                        
                        # Handle start_date
                        start_date = None
                        if 'start_date' in actual_columns:
                            raw_date = row[actual_columns['start_date']]
                            if pd.notna(raw_date):
                                try:
                                    start_date = pd.to_datetime(raw_date).date()
                                except:
                                    continue # Skip if date is invalid
                        
                        if not start_date:
                            continue # Skip rows without a valid start date

                        contract_start_date = start_date
                        if 'contract_start_date' in actual_columns:
                            raw_contract_date = row[actual_columns['contract_start_date']]
                            if pd.notna(raw_contract_date):
                                try:
                                    contract_start_date = pd.to_datetime(raw_contract_date).date()
                                except:
                                    contract_start_date = start_date

                        contract_duration_months = 12
                        if 'contract_duration_months' in actual_columns:
                            raw_duration = row[actual_columns['contract_duration_months']]
                            if pd.notna(raw_duration):
                                try:
                                    contract_duration_months = int(float(raw_duration))
                                except:
                                    contract_duration_months = 12

                        # Get or create department
                        department = None
                        if department_name:
                            department, _ = Department.objects.get_or_create(
                                name=department_name,
                                defaults={'email': 'muhammad.hamza@giki.edu.pk', 'description': ''}
                            )

                        # Create employee
                        employee, created = Employee.objects.get_or_create(
                            employee_id=employee_id,
                            defaults={
                                'name': name,
                                'designation': designation,
                                'department': department,
                                'start_date': start_date,
                                'contract_start_date': contract_start_date,
                                'contract_duration_months': contract_duration_months,
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            # Update existing employee info if needed? 
                            # For now, just skip to avoid accidental overwrites
                            pass

                    except Exception as row_error:
                        print(f"Error at row {index}: {row_error}")
                        continue

                messages.success(request, f'Successfully imported {created_count} employees from Excel file.')
                return redirect('employee_list')
            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f'Error importing Excel file: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeUploadForm()

    return render(request, 'hr_portal/import_employees.html', {'form': form})

@login_required
def export_employees_to_excel(request):
    """Export employees to Excel file"""
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO

    # Get all employees
    employees = Employee.objects.all()

    # Prepare data for Excel
    data = []
    for emp in employees:
        data.append({
            'Employee ID': emp.employee_id,
            'Name': emp.name,
            'Designation': emp.designation,
            'Department': emp.department.name if emp.department else '',
            'Start Date': emp.start_date,
            'End Date': emp.end_date,
            'Probation Status': emp.probation_status,
            'Days Until Probation End': emp.days_until_probation_end,
        })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create Excel file in memory
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Employees', index=False)

    buffer.seek(0)

    # Create HTTP response
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=employees_export.xlsx'

    return response

@login_required
def employee_edit(request, employee_id):
    """Edit an existing employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.name} updated successfully!')
            return redirect('employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'hr_portal/employee_form.html', {'form': form, 'employee': employee})

@login_required
def employee_delete(request, employee_id):
    """Delete an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        employee.delete()
        messages.success(request, f'Employee {employee.name} deleted successfully!')
        return redirect('employee_list')

    return render(request, 'hr_portal/employee_confirm_delete.html', {'employee': employee})

@login_required
def send_department_email(request, employee_id):
    """Send department email for an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        # Get department email
        dept_email = employee.department.email if employee.department else None
        if not dept_email:
            messages.error(request, f'No email configured for {employee.department.name if employee.department else "this employee\'s department"}.')
            return redirect('employee_list')

        # Prepare email content
        subject = f"Notification: {employee.name} - Probation Period Update"
        message = f"""
        Dear Department Head,

        This is to inform you that {employee.name} (Employee ID: {employee.employee_id})
        in the {employee.department.name if employee.department else 'N/A'} department
        has a probation period update.

        Current status: {employee.probation_status}
        Days until probation ends: {employee.days_until_probation_end}

        Please take the necessary action as required.

        Best regards,
        HR Department
        """

        try:
            from django.core.mail import send_mail
            from django.conf import settings

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [dept_email],
                fail_silently=False,
            )

            messages.success(request, f'Department email sent successfully to {dept_email} for {employee.name}.')
        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')

        return redirect('employee_list')

    return render(request, 'hr_portal/send_department_email.html', {'employee': employee})

@login_required
def document_management(request):
    """Manage all documents"""
    documents = EmployeeDocument.objects.all().order_by('-uploaded_at')
    return render(request, 'hr_portal/document_management.html', {'documents': documents})

@login_required
def upload_document_ajax(request):
    """AJAX endpoint for uploading documents"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        title = request.POST.get('title')
        document_type = request.POST.get('document_type', 'other')
        description = request.POST.get('description', '')
        employee_id = request.POST.get('employee_id')
        file = request.FILES.get('file')

        if file and title:
            try:
                employee = get_employee_by_id(employee_id) if employee_id else None
                document = EmployeeDocument.objects.create(
                    employee=employee,
                    title=title,
                    document_type=document_type,
                    file=file,
                    description=description
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Document uploaded successfully!',
                    'document_id': document.id
                })
            except Employee.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Employee not found.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please provide a title and file.'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    })

@login_required
def download_document(request, document_id):
    """Download a specific document"""
    document = EmployeeDocument.objects.get(pk=document_id)

    if document.file:
        from django.http import FileResponse
        import os

        file_path = document.file.path
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
        else:
            messages.error(request, 'Document file not found.')
            return redirect('documents')
    else:
        messages.error(request, 'No file associated with this document.')
        return redirect('documents')

@login_required
def ai_assistant(request):
    """AI Assistant interface"""
    return render(request, 'hr_portal/ai_assistant.html')

@login_required
def get_employees_api(request):
    """API endpoint to get employees"""
    employees = Employee.objects.all()
    employee_data = []
    for emp in employees:
        employee_data.append({
            'id': emp.employee_id,
            'name': emp.name,
            'designation': emp.designation,
            'department': emp.department.name if emp.department else 'N/A',
            'start_date': emp.start_date.isoformat(),
            'end_date': emp.end_date.isoformat() if emp.end_date else None,
            'probation_status': emp.probation_status,
            'days_until_probation_end': emp.days_until_probation_end
        })

    return JsonResponse({'employees': employee_data})

@login_required
def template_management(request):
    """Manage document templates"""
    templates = DocumentTemplate.objects.all()
    return render(request, 'hr_portal/template_management.html', {'templates': templates})

@login_required
def template_edit(request, template_id):
    """Edit a document template"""
    template = DocumentTemplate.objects.get(pk=template_id)

    if request.method == 'POST':
        template.name = request.POST.get('name')
        template.description = request.POST.get('description', '')
        template.is_active = request.POST.get('is_active') == 'on'

        if 'template_file' in request.FILES:
            template.template_file = request.FILES['template_file']

        template.save()
        messages.success(request, f'Template "{template.name}" updated successfully!')
        return redirect('template_management')

    return render(request, 'hr_portal/template_form.html', {'template': template})

@login_required
def template_delete(request, template_id):
    """Delete a document template"""
    template = DocumentTemplate.objects.get(pk=template_id)
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f'Template "{template_name}" deleted successfully!')
        return redirect('template_management')

    return render(request, 'hr_portal/template_confirm_delete.html', {'template': template})

@login_required
def template_content_edit(request, template_id):
    """Edit template content"""
    template = DocumentTemplate.objects.get(pk=template_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        # This would typically update the template file content
        # For now, we'll just show a success message
        messages.success(request, f'Template "{template.name}" content updated successfully!')
        return redirect('template_management')

    return render(request, 'hr_portal/template_content_editor.html', {'template': template})

@login_required
def generate_document_from_template(request, employee_id, template_id):
    """Generate a document from a template for an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, 'Employee not found.')
        return redirect('employee_list')

    template = DocumentTemplate.objects.get(pk=template_id)

    # This would typically generate a document using the template
    # For now, we'll create a simple document
    from django.core.files.base import ContentFile
    import tempfile
    import os

    if request.method == 'POST':
        # Generate document content based on template
        content = f"""
        {template.name.upper()}

        TO: {employee.name} (ID: {employee.employee_id})
        DESIGNATION: {employee.designation}
        DEPARTMENT: {employee.department.name if employee.department else 'N/A'}

        DATE: {timezone.now().date()}

        CONTENT: This is a generated document based on the {template.name} template.
        """

        # Create a temporary file with the content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Create an EmployeeDocument object
        from django.core.files import File
        with open(tmp_file_path, 'rb') as f:
            doc = EmployeeDocument.objects.create(
                employee=employee,
                title=f"{template.name} - {employee.name}",
                document_type='other',
                description=f"Generated from {template.name} template",
            )
            doc.file.save(f"{template.name}_{employee.employee_id}.txt", File(f))

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        messages.success(request, f'Document generated from template "{template.name}" for {employee.name} successfully!')
        return redirect('employee_documents', employee_id=employee.id)

    return render(request, 'hr_portal/generate_from_template.html', {
        'employee': employee,
        'template': template
    })

@login_required
def probation_approval(request, employee_id):
    """Handle probation approval for an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        comments = request.POST.get('comments', '')

        # Create or update probation approval record
        approval, created = ProbationApproval.objects.get_or_create(
            employee=employee,
            defaults={
                'approval_status': approval_status,
                'requested_by': request.user.username,
                'comments': comments
            }
        )

        if not created:
            approval.approval_status = approval_status
            approval.comments = comments
            approval.updated_at = timezone.now()
            approval.save()

        messages.success(request, f'Probation approval status updated to {approval.get_approval_status_display()} for {employee.name}.')
        return redirect('employee_list')

    return render(request, 'hr_portal/probation_approval.html', {'employee': employee})

@login_required
def probation_noting(request, employee_id):
    """Handle probation noting for an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    # This would typically handle noting of probation status
    messages.info(request, f'Probation noting functionality for {employee.name} would be implemented here.')
    return redirect('employee_list')

@login_required
def probation_letter(request, employee_id):
    """Generate probation letter for an employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        messages.error(request, f'Employee with ID {employee_id} not found.')
        return redirect('employee_list')

    # This would typically generate a probation letter
    content = f"""
    PROBATION LETTER

    TO: {employee.name} (ID: {employee.employee_id})
    DESIGNATION: {employee.designation}
    DEPARTMENT: {employee.department.name if employee.department else 'N/A'}

    PERIOD: {employee.start_date} to {employee.end_date}

    This letter confirms the probationary period for the above mentioned employee.
    """

    # Create a temporary file with the content
    import tempfile
    import os
    from django.core.files.base import ContentFile
    from django.core.files import File

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    # Create an EmployeeDocument object
    with open(tmp_file_path, 'rb') as f:
        doc = EmployeeDocument.objects.create(
            employee=employee,
            title=f"Probation Letter - {employee.name}",
            document_type='other',
            description="Probation letter generated automatically",
        )
        doc.file.save(f"probation_letter_{employee.employee_id}.txt", File(f))

    # Clean up the temporary file
    os.unlink(tmp_file_path)

    messages.success(request, f'Probation letter generated for {employee.name} successfully!')
    return redirect('employee_documents', employee_id=employee.id)

@login_required
def generate_probation_confirmation_letter(request, employee_id):
    """Generate probation confirmation letter for an employee"""
    # Convert employee_id to integer if it's a float (e.g., "67.0" -> 67)
    try:
        employee_id = int(float(employee_id))  # Handles both "67" and "67.0"
    except (ValueError, TypeError):
        messages.error(request, 'Invalid employee ID.')
        return redirect('employee_list')

    employee = Employee.objects.get(pk=employee_id)

    # This would typically generate a confirmation letter
    content = f"""
    PROBATION CONFIRMATION LETTER

    TO: {employee.name} (ID: {employee.employee_id})
    DESIGNATION: {employee.designation}
    DEPARTMENT: {employee.department.name if employee.department else 'N/A'}

    DATE: {timezone.now().date()}

    This letter confirms that your probation period has been successfully completed.
    """

    # Create a temporary file with the content
    import tempfile
    import os
    from django.core.files.base import ContentFile
    from django.core.files import File

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    # Create an EmployeeDocument object
    with open(tmp_file_path, 'rb') as f:
        doc = EmployeeDocument.objects.create(
            employee=employee,
            title=f"Probation Confirmation - {employee.name}",
            document_type='other',
            description="Probation confirmation letter",
        )
        doc.file.save(f"probation_confirmation_{employee.employee_id}.txt", File(f))

    # Clean up the temporary file
    os.unlink(tmp_file_path)

    messages.success(request, f'Probation confirmation letter generated for {employee.name} successfully!')
    return redirect('employee_documents', employee_id=employee.id)

@login_required
def generate_probation_extension_letter(request, employee_id):
    """Generate probation extension letter for an employee"""
    # Convert employee_id to integer if it's a float (e.g., "67.0" -> 67)
    try:
        employee_id = int(float(employee_id))  # Handles both "67" and "67.0"
    except (ValueError, TypeError):
        messages.error(request, 'Invalid employee ID.')
        return redirect('employee_list')

    employee = Employee.objects.get(pk=employee_id)

    # This would typically generate an extension letter
    content = f"""
    PROBATION EXTENSION LETTER

    TO: {employee.name} (ID: {employee.employee_id})
    DESIGNATION: {employee.designation}
    DEPARTMENT: {employee.department.name if employee.department else 'N/A'}

    DATE: {timezone.now().date()}

    This letter confirms that your probation period has been extended.
    """

    # Create a temporary file with the content
    import tempfile
    import os
    from django.core.files.base import ContentFile
    from django.core.files import File

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    # Create an EmployeeDocument object
    with open(tmp_file_path, 'rb') as f:
        doc = EmployeeDocument.objects.create(
            employee=employee,
            title=f"Probation Extension - {employee.name}",
            document_type='other',
            description="Probation extension letter",
        )
        doc.file.save(f"probation_extension_{employee.employee_id}.txt", File(f))

    # Clean up the temporary file
    os.unlink(tmp_file_path)

    messages.success(request, f'Probation extension letter generated for {employee.name} successfully!')
    return redirect('employee_documents', employee_id=employee.id)

@login_required
def send_probation_notification_email(request):
    """Send custom probation notification emails"""
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json

    if request.method == 'POST':
        try:
            # Get data from POST request
            employee_id = request.POST.get('employee_id')
            recipient_email = request.POST.get('recipient_email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            # Validate required fields (subject and message can have defaults if not provided)
            if not employee_id or not recipient_email:
                return JsonResponse({'success': False, 'error': 'Missing required fields: employee_id or recipient_email'})

            # Get employee - handle potential .0 in ID
            employee = None
            possible_ids = [str(employee_id)]
            try:
                # If it's something like "200.0", also try "200"
                if '.' in str(employee_id):
                    float_id = float(employee_id)
                    if float_id.is_integer():
                        possible_ids.append(str(int(float_id)))
                else:
                    # If it's something like "200", also try "200.0"
                    int_id = int(employee_id)
                    possible_ids.append(f"{int_id}.0")
            except (ValueError, TypeError):
                pass

            for eid in possible_ids:
                try:
                    employee = Employee.objects.get(employee_id=eid)
                    break
                except Employee.DoesNotExist:
                    continue

            if not employee:
                return JsonResponse({'success': False, 'error': f'Employee with ID {employee_id} not found'})

            # Set defaults for subject and message if missing
            if not subject:
                subject = f"Probation Notification: {employee.name}"
            
            if not message:
                message = f"This is a notification regarding the probation period for {employee.name} (ID: {employee.employee_id})."

            # Send email
            from django.core.mail import send_mail
            from django.conf import settings

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': 'Email sent successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def probation_approval_ajax(request, employee_id):
    """AJAX endpoint for probation approval"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        employee = get_employee_by_id(employee_id)
        if not employee:
            return JsonResponse({'success': False, 'message': 'Employee not found.'})

        if request.method == 'POST':
            action = request.POST.get('action', '').lower()
            comments = request.POST.get('comments', '')
            extension_months = request.POST.get('extension_months', 3)

            # Map action to approval status
            status_mapping = {
                'approve': 'approved',
                'reject': 'rejected',
                'extend': 'extended'
            }

            approval_status = status_mapping.get(action, 'pending')

            # Create or update probation approval record
            approval, created = ProbationApproval.objects.get_or_create(
                employee=employee,
                defaults={
                    'approval_status': approval_status,
                    'requested_by': request.user.username,
                    'comments': comments
                }
            )

            if not created:
                approval.approval_status = approval_status
                approval.comments = comments
                approval.updated_at = timezone.now()

                # Handle extension - update employee's end date
                if action == 'extend':
                    try:
                        import datetime
                        from django.utils import timezone
                        current_end_date = employee.end_date
                        new_end_date = current_end_date + datetime.timedelta(days=int(extension_months) * 30)
                        employee.end_date = new_end_date
                        employee.is_extended = True
                        employee.save()

                        # Update the approval record with extension info
                        approval.extension_months = int(extension_months)
                        approval.extended_end_date = new_end_date

                    except (ValueError, TypeError):
                        return JsonResponse({'success': False, 'message': 'Invalid extension period.'})

                approval.save()

            # Update employee's probation status based on approval
            if action == 'approve':
                employee.probation_status = 'Completed'
            elif action == 'reject':
                employee.probation_status = 'Rejected'
            elif action == 'extend':
                employee.probation_status = 'Extended'

            employee.save()

            response_data = {
                'success': True,
                'message': f'Probation approval status updated to {approval.get_approval_status_display()}',
                'action': action
            }

            # Include extended end date in response if applicable
            if action == 'extend' and hasattr(approval, 'extended_end_date') and approval.extended_end_date:
                response_data['extended_end_date'] = approval.extended_end_date.strftime('%Y-%m-%d')

            return JsonResponse(response_data)

    return JsonResponse({'success': False, 'message': 'Invalid request'})

# Add other views as needed...
