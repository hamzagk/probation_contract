"""
Utility functions for HR Portal
"""

def generate_document_template(document_type, employee_data, additional_info=""):
    """
    Generate a document template based on type and employee data
    """
    # This is a placeholder implementation
    # In a real application, this would contain logic to generate document templates
    
    employee_info = f"""
    Employee Information:
    - Name: {employee_data.get('name', 'N/A')}
    - Employee ID: {employee_data.get('employee_id', 'N/A')}
    - Designation: {employee_data.get('designation', 'N/A')}
    - Department: {employee_data.get('department', 'N/A')}
    - Start Date: {employee_data.get('start_date', 'N/A')}
    """
    
    if document_type == 'service_certificate':
        template = f"""
        SERVICE CERTIFICATE TEMPLATE
        
        This is to certify that {employee_data.get('name', 'N/A')} with employee ID {employee_data.get('employee_id', 'N/A')} 
        has served at GIK Institute in the capacity of {employee_data.get('designation', 'N/A')} 
        in the {employee_data.get('department', 'N/A')} department.
        
        Period of Service: {employee_data.get('start_date', 'N/A')} to Present
        
        {additional_info}
        """
    elif document_type == 'experience_certificate':
        template = f"""
        EXPERIENCE CERTIFICATE TEMPLATE
        
        This is to certify the work experience of {employee_data.get('name', 'N/A')} 
        with employee ID {employee_data.get('employee_id', 'N/A')} who worked as 
        {employee_data.get('designation', 'N/A')} in the {employee_data.get('department', 'N/A')} 
        department at GIK Institute.
        
        {additional_info}
        """
    elif document_type == 'relieving_letter':
        template = f"""
        RELIEVING LETTER TEMPLATE
        
        This letter serves as a relieving letter for {employee_data.get('name', 'N/A')} 
        with employee ID {employee_data.get('employee_id', 'N/A')} from their position 
        as {employee_data.get('designation', 'N/A')} in the {employee_data.get('department', 'N/A')} 
        department at GIK Institute.
        
        {additional_info}
        """
    else:
        template = f"""
        DOCUMENT TEMPLATE
        
        This is a generated document for {employee_data.get('name', 'N/A')} 
        with employee ID {employee_data.get('employee_id', 'N/A')}.
        
        {additional_info}
        """
    
    return template.strip()

def validate_employee_data(data):
    """
    Validate employee data before saving
    """
    errors = []
    
    if not data.get('name'):
        errors.append('Name is required')
    
    if not data.get('employee_id'):
        errors.append('Employee ID is required')
    
    if not data.get('designation'):
        errors.append('Designation is required')
    
    if not data.get('start_date'):
        errors.append('Start date is required')
    
    return errors