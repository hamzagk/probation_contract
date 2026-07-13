from datetime import date

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from hr_portal.models import Department, Employee, MonthlyProbationReportLog
from hr_portal.monthly_probation_reports import (
    build_monthly_department_reports,
    send_monthly_probation_reports,
)


class MonthlyProbationReportTests(TestCase):
    def setUp(self):
        self.report_date = date(2026, 7, 1)
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="secret123",
        )
        self.cs = Department.objects.create(
            name="Computer Science",
            email="cs.ps@giki.edu.pk",
        )
        self.ee = Department.objects.create(
            name="Electrical Engineering",
            email="ee.pa@giki.edu.pk",
        )

    def create_employee(self, employee_id, name, department, start_date, **kwargs):
        defaults = {
            "designation": "Lecturer",
            "department": department,
            "probation_status": "Active",
        }
        defaults.update(kwargs)
        return Employee.objects.create(
            employee_id=employee_id,
            name=name,
            start_date=start_date,
            **defaults,
        )

    def test_build_reports_groups_by_department_for_current_month(self):
        self.create_employee("1001", "Alice", self.cs, date(2026, 1, 15))
        self.create_employee("1002", "Bob", self.cs, date(2026, 1, 20))
        self.create_employee("2001", "Charlie", self.ee, date(2026, 1, 10))
        self.create_employee("3001", "Dana", self.ee, date(2026, 2, 5))
        self.create_employee(
            "4001",
            "Associate",
            self.cs,
            date(2026, 1, 12),
            designation="Associate Professor",
        )
        self.create_employee(
            "5001",
            "Contract Person",
            self.cs,
            date(2026, 1, 18),
            is_contract_record=True,
        )

        reports = build_monthly_department_reports(self.report_date)

        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0]["department_name"], "Computer Science")
        self.assertEqual(reports[0]["employee_count"], 2)
        self.assertEqual(reports[1]["department_name"], "Electrical Engineering")
        self.assertEqual(reports[1]["employee_count"], 1)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="hr@example.com",
        HR_EMAIL="muhammad.hamza@giki.edu.pk",
        HR_EMAIL_LIST=["muhammad.hamza@giki.edu.pk", "nasirali@giki.edu.pk"],
    )
    def test_send_reports_to_test_recipient_and_log_dispatch(self):
        self.create_employee("1001", "Alice", self.cs, date(2026, 1, 15))
        self.create_employee("2001", "Charlie", self.ee, date(2026, 1, 10))

        result = send_monthly_probation_reports(
            reference_date=self.report_date,
            test_recipient="muhammad.hamza@giki.edu.pk",
        )

        self.assertEqual(result["sent_reports"], 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(all(message.to == ["muhammad.hamza@giki.edu.pk"] for message in mail.outbox))
        self.assertTrue(all(message.subject.startswith("[TEST] Monthly Probation Report") for message in mail.outbox))
        self.assertEqual(
            MonthlyProbationReportLog.objects.filter(test_mode=True).count(),
            2,
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="hr@example.com",
        HR_EMAIL="muhammad.hamza@giki.edu.pk",
        HR_EMAIL_LIST=["muhammad.hamza@giki.edu.pk"],
    )
    def test_duplicate_protection_skips_second_send(self):
        self.create_employee("1001", "Alice", self.cs, date(2026, 1, 15))

        first = send_monthly_probation_reports(
            reference_date=self.report_date,
            test_recipient="muhammad.hamza@giki.edu.pk",
        )
        second = send_monthly_probation_reports(
            reference_date=self.report_date,
            test_recipient="muhammad.hamza@giki.edu.pk",
        )

        self.assertEqual(first["sent_reports"], 1)
        self.assertEqual(second["sent_reports"], 0)
        self.assertEqual(second["skipped_reports"], 1)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="hr@example.com",
        HR_EMAIL="muhammad.hamza@giki.edu.pk",
        HR_EMAIL_LIST=["muhammad.hamza@giki.edu.pk"],
    )
    def test_dashboard_manual_send_endpoint_dispatches_reports(self):
        self.client.force_login(self.user)
        self.create_employee("1001", "Alice", self.cs, date(2026, 1, 15))
        self.create_employee("2001", "Charlie", self.ee, date(2026, 1, 10))

        response = self.client.post(reverse("send_monthly_probation_report_manual"))

        self.assertRedirects(response, reverse("probation_dashboard"))
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            sorted(message.to[0] for message in mail.outbox),
            ["cs.ps@giki.edu.pk", "ee.pa@giki.edu.pk"],
        )
        self.assertEqual(MonthlyProbationReportLog.objects.filter(test_mode=False).count(), 2)
