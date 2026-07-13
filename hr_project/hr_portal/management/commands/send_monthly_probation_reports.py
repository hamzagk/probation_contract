from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from hr_portal.monthly_probation_reports import send_monthly_probation_reports


class Command(BaseCommand):
    help = "Send department-wise monthly probation reports."

    def add_arguments(self, parser):
        parser.add_argument(
            "--test-recipient",
            default="",
            help="Override all recipients and send test copies to a single email address.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Send the report even if it has already been sent for this month.",
        )
        parser.add_argument(
            "--month",
            default="",
            help="Month to report in YYYY-MM format. Defaults to the current month.",
        )

    def handle(self, *args, **options):
        report_date = None
        month_value = options["month"].strip()
        if month_value:
            try:
                report_date = datetime.strptime(f"{month_value}-01", "%Y-%m-%d").date()
            except ValueError as exc:
                raise CommandError("Invalid --month value. Use YYYY-MM.") from exc

        test_recipient = options["test_recipient"].strip() or getattr(
            settings,
            "MONTHLY_PROBATION_REPORT_TEST_RECIPIENT",
            "",
        )
        if not options["test_recipient"]:
            test_recipient = ""

        result = send_monthly_probation_reports(
            reference_date=report_date,
            test_recipient=test_recipient or None,
            force=options["force"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Monthly report month: {result['report_month_label']} | "
                f"sent: {result['sent_reports']} | skipped: {result['skipped_reports']}"
            )
        )

        for report in result["reports"]:
            status = "SENT" if report["sent"] else "SKIPPED"
            self.stdout.write(
                f"{status}: {report['department_name']} -> {report['delivery_email']} "
                f"({report['employee_count']} employee(s))"
            )
