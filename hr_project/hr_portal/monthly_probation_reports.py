from calendar import monthrange

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from hr_portal.models import Employee, MonthlyProbationReportLog


def get_report_month_bounds(reference_date=None):
    reference_date = reference_date or timezone.localdate()
    month_start = reference_date.replace(day=1)
    month_end = month_start.replace(day=monthrange(month_start.year, month_start.month)[1])
    return month_start, month_end


def get_monthly_probation_queryset(reference_date=None):
    month_start, month_end = get_report_month_bounds(reference_date)
    return (
        Employee.objects.select_related("department")
        .filter(is_contract_record=False)
        .exclude(designation__icontains="Associate Professor")
        .exclude(probation_status__in=["Completed", "Rejected"])
        .filter(
            Q(is_extended=True, extended_probation_end_date__range=[month_start, month_end])
            | (
                (Q(is_extended=False) | Q(extended_probation_end_date__isnull=True))
                & Q(end_date__range=[month_start, month_end])
            )
        )
        .order_by("department__name", "end_date", "name")
    )


def build_monthly_department_reports(reference_date=None):
    report_date = reference_date or timezone.localdate()
    month_start, month_end = get_report_month_bounds(report_date)
    fallback_email = getattr(
        settings,
        "HR_EMAIL",
        getattr(settings, "DEFAULT_FROM_EMAIL", "muhammad.hamza@giki.edu.pk"),
    )

    reports = []
    current_report = None
    current_key = None

    for employee in get_monthly_probation_queryset(reference_date):
        department = employee.department
        department_name = department.name if department else "Unassigned Department"
        recipient_email = department.email if department and department.email else fallback_email
        report_key = (department.pk if department else None, department_name, recipient_email)

        if report_key != current_key:
            current_report = {
                "department": department,
                "department_name": department_name,
                "recipient_email": recipient_email,
                "employees": [],
                "employee_count": 0,
                "month_start": month_start,
                "month_end": month_end,
                "month_label": month_start.strftime("%B %Y"),
            }
            reports.append(current_report)
            current_key = report_key

        current_end_date = employee.current_end_date
        total_probation_days = max((current_end_date - employee.start_date).days, 1)
        days_completed = max(min((report_date - employee.start_date).days, total_probation_days), 0)
        progress_percentage = round((days_completed / total_probation_days) * 100)

        current_report["employees"].append(
            {
                "id": str(employee.employee_id).removesuffix(".0"),
                "name": employee.name,
                "designation": employee.designation,
                "department": department_name,
                "start_date": employee.start_date.strftime("%B %d, %Y"),
                "end_date": current_end_date.strftime("%B %d, %Y"),
                "days_until_probation_end": (current_end_date - report_date).days,
                "probation_completion_percent": progress_percentage,
                "is_extended": employee.is_extended,
            }
        )
        current_report["employee_count"] += 1

    return reports


def send_monthly_probation_reports(reference_date=None, test_recipient=None, force=False):
    report_date = reference_date or timezone.localdate()
    month_start, _ = get_report_month_bounds(report_date)
    reports = build_monthly_department_reports(report_date)
    hr_contact = getattr(settings, "HR_EMAIL", getattr(settings, "DEFAULT_FROM_EMAIL", "HR Department"))
    cc_emails = []
    for email in getattr(settings, "HR_EMAIL_LIST", []):
        if email and email not in cc_emails:
            cc_emails.append(email)
    if hr_contact and hr_contact not in cc_emails:
        cc_emails.insert(0, hr_contact)

    summary = {
        "report_month": month_start.isoformat(),
        "report_month_label": month_start.strftime("%B %Y"),
        "total_departments": len(reports),
        "sent_reports": 0,
        "skipped_reports": 0,
        "reports": [],
    }

    for report in reports:
        department_name = report["department_name"]
        delivery_email = test_recipient or report["recipient_email"]
        already_sent = MonthlyProbationReportLog.objects.filter(
            report_month=month_start,
            department_name=department_name,
            recipient_email=delivery_email,
            test_mode=bool(test_recipient),
        ).exists()

        report_result = {
            "department_name": department_name,
            "recipient_email": report["recipient_email"],
            "delivery_email": delivery_email,
            "employee_count": report["employee_count"],
            "skipped": False,
            "sent": False,
        }

        if already_sent and not force:
            report_result["skipped"] = True
            summary["skipped_reports"] += 1
            summary["reports"].append(report_result)
            continue

        context = {
            "employees": report["employees"],
            "current_date": report_date.strftime("%B %d, %Y"),
            "report_title": f"Monthly Probation Report - {department_name}",
            "report_period": f"{report['month_start'].strftime('%B %d, %Y')} to {report['month_end'].strftime('%B %d, %Y')}",
            "report_month_label": report["month_label"],
            "department_name": department_name,
            "employee_count": report["employee_count"],
            "hr_contact": hr_contact,
            "is_test_email": bool(test_recipient),
            "intended_recipient": report["recipient_email"],
        }
        html_message = render_to_string("hr_portal/probation_report_email.html", context)
        subject_prefix = "[TEST] " if test_recipient else ""
        subject = (
            f"{subject_prefix}Monthly Probation Report - {department_name} - "
            f"{report['month_label']}"
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=(
                f"Monthly probation report for {department_name} covering {report['month_label']}. "
                "Please view this message in an HTML-compatible email client."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[delivery_email],
            cc=[] if test_recipient else cc_emails,
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        MonthlyProbationReportLog.objects.create(
            report_month=month_start,
            department=report["department"],
            department_name=department_name,
            recipient_email=delivery_email,
            employee_count=report["employee_count"],
            test_mode=bool(test_recipient),
        )

        report_result["sent"] = True
        summary["sent_reports"] += 1
        summary["reports"].append(report_result)

    return summary
