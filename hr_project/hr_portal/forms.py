from django import forms
from dateutil.relativedelta import relativedelta
from .models import Employee, Department, EmployeeDocument

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'name',
            'designation',
            'department',
            'start_date',
            'contract_start_date',
            'contract_duration_months',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_duration_months': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'Enter employee ID', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter employee name', 'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Enter designation', 'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure department queryset is all departments ordered by name
        self.fields['department'].queryset = Department.objects.order_by('name')
        self.fields['department'].empty_label = "--------- Select a department ---------"
        self.fields['department'].required = False

    def save(self, commit=True):
        employee = super().save(commit=False)
        contract_changed = employee.pk is None or any(
            field in self.changed_data for field in ['contract_start_date', 'contract_duration_months']
        )
        if employee.contract_start_date and contract_changed:
            employee.contract_end_date = employee.contract_start_date + relativedelta(
                months=employee.contract_duration_months
            )
        elif not employee.contract_start_date:
            employee.contract_end_date = None
        if commit:
            employee.save()
            self.save_m2m()
        return employee

class EmployeeUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select Excel file',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )

class ContractImportForm(forms.Form):
    contract_file = forms.FileField(
        label='Select Word or Excel file',
        widget=forms.FileInput(attrs={'accept': '.docx,.xlsx,.xls'})
    )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['title', 'document_type', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter document title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter description'}),
        }
