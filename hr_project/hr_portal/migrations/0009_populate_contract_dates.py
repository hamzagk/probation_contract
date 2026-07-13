from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import migrations


def populate_contract_dates(apps, schema_editor):
    Employee = apps.get_model("hr_portal", "Employee")
    today = date.today()

    for employee in Employee.objects.filter(contract_start_date__isnull=True):
        contract_start_date = employee.start_date
        contract_duration_months = employee.contract_duration_months or 12
        contract_end_date = contract_start_date + relativedelta(months=contract_duration_months)

        if contract_end_date < today:
            contract_status = "expired"
        elif (contract_end_date - today).days <= 60:
            contract_status = "expiring_soon"
        else:
            contract_status = "active"

        employee.contract_start_date = contract_start_date
        employee.contract_duration_months = contract_duration_months
        employee.contract_end_date = contract_end_date
        employee.contract_status = contract_status
        employee.save(update_fields=[
            "contract_start_date",
            "contract_duration_months",
            "contract_end_date",
            "contract_status",
        ])


def clear_populated_contract_dates(apps, schema_editor):
    Employee = apps.get_model("hr_portal", "Employee")
    Employee.objects.update(
        contract_start_date=None,
        contract_end_date=None,
        contract_status="active",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("hr_portal", "0008_alter_department_options_alter_employee_options_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_contract_dates, clear_populated_contract_dates),
    ]
