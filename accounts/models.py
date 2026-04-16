from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
        (ADMIN, 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PATIENT)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    current_medications = models.TextField(blank=True, help_text='List of medications currently in use')

    def __str__(self):
        return self.user.get_full_name() or self.user.username
