from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models


def employee_document_upload_path(instance, filename):
    employee_id = getattr(instance.employee, "employee_id", "general")
    return f"employees/{employee_id}/{filename}"


def template_upload_path(instance, filename):
    return f"templates/{filename}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(help_text="Email address for department head")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    PROBATION_STATUS_CHOICES = [
        ("Active", "Active"),
        ("Ending Soon", "Ending Soon"),
        ("Completed", "Completed"),
        ("Extended", "Extended"),
        ("Rejected", "Rejected"),
    ]

    CONTRACT_STATUS_CHOICES = [
        ("active", "Active"),
        ("expiring_soon", "Expiring Soon"),
        ("expired", "Expired"),
        ("renewed", "Renewed"),
    ]

    employee_id = models.CharField(max_length=20, unique=True, verbose_name="S.#")
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField(editable=False)
    probation_status = models.CharField(
        max_length=20,
        choices=PROBATION_STATUS_CHOICES,
        default="Active",
    )
    is_extended = models.BooleanField(
        default=False,
        help_text="Indicates if the probation period has been extended",
    )
    extended_probation_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="New end date if probation is extended",
    )

    contract_start_date = models.DateField(null=True, blank=True)
    contract_duration_months = models.PositiveIntegerField(default=12)
    contract_end_date = models.DateField(null=True, blank=True, editable=False)
    contract_status = models.CharField(
        max_length=20,
        choices=CONTRACT_STATUS_CHOICES,
        default="active",
    )
    is_contract_record = models.BooleanField(
        default=False,
        help_text="Tracks employees managed through the contract renewal module",
    )
    is_contract_extended = models.BooleanField(
        default=False,
        help_text="Indicates if the contract period has been extended",
    )
    extended_contract_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="New end date if contract is extended",
    )

    class Meta:
        ordering = ["-start_date", "name"]

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + relativedelta(months=6)

        if self.contract_start_date:
            if not self.contract_end_date:
                self.contract_end_date = self.contract_start_date + relativedelta(
                    months=self.contract_duration_months
                )
            current_contract_end = self.current_contract_end_date
            if current_contract_end < date.today():
                self.contract_status = "expired"
            elif (current_contract_end - date.today()).days <= 60:
                self.contract_status = "expiring_soon"
            elif self.contract_status not in ["renewed", "expired"]:
                self.contract_status = "active"

        if not self.has_probation:
            self.probation_status = "Completed"
        elif self.probation_status == "Rejected":
            pass
        else:
            current_end_date = self.current_end_date
            if current_end_date < date.today():
                self.probation_status = "Completed"
            elif self.is_extended:
                self.probation_status = "Extended"
            elif self.is_probation_ending_soon:
                self.probation_status = "Ending Soon"
            else:
                self.probation_status = "Active"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    @property
    def has_probation(self):
        return "Associate Professor" not in self.designation

    @property
    def current_end_date(self):
        return self.extended_probation_end_date if self.is_extended and self.extended_probation_end_date else self.end_date

    @property
    def days_until_probation_end(self):
        if not self.has_probation:
            return 0
        return (self.current_end_date - date.today()).days

    @property
    def is_probation_ending_soon(self):
        if not self.has_probation:
            return False
        days_remaining = self.days_until_probation_end
        return 0 <= days_remaining <= 30

    @property
    def probation_completion_percent(self):
        if not self.has_probation:
            return 100
        total_probation_days = 180
        days_completed = total_probation_days - self.days_until_probation_end
        percent = (days_completed / total_probation_days) * 100
        return min(100, max(0, round(percent)))

    @property
    def has_contract(self):
        return self.contract_start_date is not None

    @property
    def current_contract_end_date(self):
        if not self.has_contract:
            return None
        if self.is_contract_extended and self.extended_contract_end_date:
            return self.extended_contract_end_date
        return self.contract_end_date

    @property
    def contract_duration_label(self):
        if not self.contract_duration_months:
            return "N/A"
        years, months = divmod(self.contract_duration_months, 12)
        parts = []
        if years:
            parts.append(f"{years} year" if years == 1 else f"{years} years")
        if months:
            parts.append(f"{months} month" if months == 1 else f"{months} months")
        return " ".join(parts) if parts else "0 months"

    @property
    def days_until_contract_end(self):
        if not self.current_contract_end_date:
            return 0
        return (self.current_contract_end_date - date.today()).days

    @property
    def is_contract_ending_soon(self):
        if not self.has_contract:
            return False
        days_remaining = self.days_until_contract_end
        return 0 <= days_remaining <= 60


class DocumentTemplate(models.Model):
    DOCUMENT_TYPES = [
        ("probation_letter", "Probation Letter"),
        ("service_certificate", "Service Certificate"),
        ("experience_certificate", "Experience Certificate"),
        ("probation_note", "Probation Note"),
        ("offer_letter", "Offer Letter"),
        ("appointment_letter", "Appointment Letter"),
        ("termination_letter", "Termination Letter"),
        ("transfer_letter", "Transfer Letter"),
        ("promotion_letter", "Promotion Letter"),
        ("salary_increment_letter", "Salary Increment Letter"),
        ("probation_extension_letter", "Probation Extension Letter"),
        ("probation_confirmation_letter", "Probation Confirmation Letter"),
        ("probation_draft", "Probation Draft"),
        ("probation_evaluation_form", "Probation Evaluation Form"),
        ("warning_letter", "Warning Letter"),
        ("resignation_acceptance_letter", "Resignation Acceptance Letter"),
        ("resignation_draft", "Resignation Draft"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=35, choices=DOCUMENT_TYPES)
    template_file = models.FileField(upload_to=template_upload_path)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ("excel", "Excel"),
        ("word", "Word"),
        ("pdf", "PDF"),
        ("other", "Other"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=employee_document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.employee.name}"


class GeneratedDocument(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="generated_documents",
    )
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE)
    document_file = models.FileField(upload_to=employee_document_upload_path)
    generated_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.employee.name}"


class ProbationApproval(models.Model):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXTENDED = "extended"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (EXTENDED, "Extended"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    approval_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    requested_by = models.CharField(max_length=100, blank=True)
    approved_by = models.CharField(max_length=100, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extension_months = models.IntegerField(
        default=0,
        help_text="Number of months to extend probation",
    )
    extended_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="New end date after extension",
    )

    def __str__(self):
        return f"{self.employee.name} - {self.get_approval_status_display()}"


class ProbationNotification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    notification_date = models.DateTimeField(auto_now_add=True)
    days_before_expiry = models.IntegerField()
    sent = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, default="probation_reminder")

    def __str__(self):
        return f"Notification for {self.employee.name} - {self.days_before_expiry} days before expiry"


class MonthlyProbationReportLog(models.Model):
    report_month = models.DateField(help_text="First day of the month covered by the report")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    department_name = models.CharField(max_length=100)
    recipient_email = models.EmailField()
    employee_count = models.PositiveIntegerField(default=0)
    test_mode = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at", "department_name"]
        indexes = [
            models.Index(fields=["report_month", "department_name", "test_mode"]),
        ]

    def __str__(self):
        return f"{self.department_name} monthly report for {self.report_month:%B %Y}"
