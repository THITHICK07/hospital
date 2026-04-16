from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Patient
from doctors.models import Doctor, DoctorAvailability


class Appointment(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    date = models.DateField()
    time_slot = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        doctor_name = self.doctor.user.get_full_name() if self.doctor else 'No Doctor'
        return f"{self.patient} - {doctor_name} - {self.date}"

    def clean(self):
        if self.doctor:
            slot_available = DoctorAvailability.objects.filter(
                doctor=self.doctor,
                date=self.date,
                time_slot=self.time_slot,
                is_available=True,
            ).exists()

            if self.status != self.CANCELLED and not slot_available and not self.pk:
                raise ValidationError('This slot is not available.')

            duplicate = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                time_slot=self.time_slot,
            ).exclude(status=self.CANCELLED)
            if self.pk:
                duplicate = duplicate.exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError('This appointment slot is already booked.')
