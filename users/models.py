from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User with role-based access."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        STAFF = 'staff', 'Staff'
        TECHNICIAN = 'technician', 'Technician'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN
