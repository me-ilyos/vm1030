from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class UniversityUser(AbstractUser):
    ROLES = (
        ("SA", "Super Admin"),
        ("DA", "Department Admin"),
        ("DU", "Department User"),
    )

    role = models.CharField(max_length=2, choices=ROLES, db_index=True)
    phone_number = models.CharField(max_length=12, unique=True)


class SuperAdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="superadmin_profile",
    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class DepartmentAdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="department_admin_profile",
    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    department_admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_of_department",
    )
    code = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name + self.code


class DepartmentUserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="regular_user_profile",
    )
    birthdate = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="members"
    )
    base_salary = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class WorkCategory(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    description = models.TextField(blank=True)
    max_percentage = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class Requirement(models.Model):
    work_category = models.ForeignKey(
        WorkCategory, on_delete=models.CASCADE, related_name="requirements"
    )
    name = models.CharField(max_length=1000, blank=True, null=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    max_percentage_increase = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name


fs = FileSystemStorage(location="uploads/professor_submissions")


class ProfessorWorkSubmission(models.Model):
    STATUS_CHOICES = (
        ("PR", "Processing"),
        ("DA", "Department Approved"),
        ("SA", "Super Approved"),
        ("DN", "Denied"),
    )
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requirement_fulfillments",
    )
    work_category = models.ForeignKey(WorkCategory, on_delete=models.CASCADE)
    requirements = models.ManyToManyField(Requirement, related_name="fulfillments")
    submission_description = models.TextField(blank=True, null=True)
    action_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PR")
    proof_file = models.FileField(
        storage=fs, upload_to="professor_submissions", blank=True
    )

    def __str__(self):
        return (
            f"{self.professor.first_name} {self.professor.last_name}"
            + f"{self.work_category.name}"
        )
