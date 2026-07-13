import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_project.settings')
django.setup()

# Import necessary modules
import pandas as pd
from hr_portal.models import Employee, Department

def import_employees_from_excel(file_path):
    """
    Import employees from Excel file directly
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        print(f"Found {len(df)} rows in the Excel file")
        print("Column names:", df.columns.tolist())
        
        # Display first few rows to understand the structure
        print("\nFirst few rows:")
        print(df.head())
        
        # Map common column names to model fields
        # Adjust these mappings based on your actual Excel file structure
        column_mapping = {
            'employee_id': ['employee_id', 'emp_id', 'id', 'employeeid'],
            'name': ['name', 'full_name', 'fullname', 'employee_name', 'employee_name'],
            'designation': ['designation', 'position', 'job_title', 'title', 'role'],
            'department': ['department', 'dept', 'division'],
            'start_date': ['start_date', 'hire_date', 'joining_date', 'date_joined', 'start_date']
        }
        
        # Find actual column names in the Excel file
        actual_columns = {}
        for model_field, possible_names in column_mapping.items():
            for name in possible_names:
                if name in df.columns.str.lower():
                    # Find the actual column name (case-sensitive)
                    actual_col = [col for col in df.columns if col.lower() == name][0]
                    actual_columns[model_field] = actual_col
                    print(f"Mapped '{model_field}' to column '{actual_col}'")
                    break
            else:
                print(f"Warning: Could not find column for '{model_field}'")
        
        if not actual_columns:
            print("Error: Could not identify any required columns in the Excel file")
            return
        
        # Import the data
        imported_count = 0
        for index, row in df.iterrows():
            try:
                # Get values from the mapped columns
                employee_id = str(row[actual_columns.get('employee_id', 'employee_id')]).strip() if 'employee_id' in actual_columns else f"EMP{index+1:04d}"
                name = str(row[actual_columns.get('name', 'name')]).strip() if 'name' in actual_columns else f"Employee {index+1}"
                designation = str(row[actual_columns.get('designation', 'designation')]).strip() if 'designation' in actual_columns else "General Staff"
                department_name = str(row[actual_columns.get('department', 'department')]).strip() if 'department' in actual_columns else "General"
                
                # Handle start_date - try different formats
                start_date_val = None
                if 'start_date' in actual_columns:
                    start_date_raw = row[actual_columns['start_date']]
                    if pd.notna(start_date_raw):
                        if isinstance(start_date_raw, str):
                            # Try to parse different date formats
                            import datetime
                            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                                try:
                                    start_date_val = datetime.datetime.strptime(str(start_date_raw), fmt).date()
                                    break
                                except ValueError:
                                    continue
                            if start_date_val is None:
                                try:
                                    start_date_val = pd.to_datetime(start_date_raw).date()
                                except:
                                    print(f"Could not parse date: {start_date_raw}")
                                    start_date_val = datetime.date.today()
                        else:
                            try:
                                start_date_val = pd.to_datetime(start_date_raw).date()
                            except:
                                start_date_val = datetime.date.today()
                    else:
                        start_date_val = datetime.date.today()
                else:
                    start_date_val = datetime.date.today()
                
                # Get or create department
                department, created = Department.objects.get_or_create(
                    name=department_name,
                    defaults={'email': 'muhammad.hamza@giki.edu.pk', 'description': f'Default department for {department_name}'}
                )
                
                # Create employee
                employee, created = Employee.objects.get_or_create(
                    employee_id=employee_id,
                    defaults={
                        'name': name,
                        'designation': designation,
                        'department': department,
                        'start_date': start_date_val
                    }
                )
                
                if created:
                    print(f"Created employee: {employee.name} (ID: {employee.employee_id})")
                    imported_count += 1
                else:
                    print(f"Employee with ID {employee.employee_id} already exists")
                    
            except Exception as e:
                print(f"Error importing row {index+1}: {e}")
                continue
        
        print(f"\nSuccessfully imported {imported_count} new employees")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    import_employees_from_excel("New employee joining-probation import.xlsx")