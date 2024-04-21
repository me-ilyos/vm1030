from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class UniversityUser(AbstractUser):
    ROLES = (
        ("SA", "Super Admin"),
        ("DA", "Department Admin"),
        ("DU", "Department User"),
    )

    role = models.CharField(max_length=2, choices=ROLES, db_index=True)


class SuperAdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="superadmin_profile",
    )
    phone_number = models.CharField(max_length=12, unique=True)


class DepartmentAdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="department_admin_profile",
    )


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

    def __str__(self):
        return self.name


class RegularUserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="regular_user_profile",
    )
    phone_number = models.CharField(max_length=20, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="members"
    )
