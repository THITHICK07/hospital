from django.db import models
from django.utils import timezone


class Payment(models.Model):
    PENDING = 'Pending'
    PAID = 'Paid'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
    )

    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    def mark_as_paid(self):
        self.status = self.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at'])

    def __str__(self):
        return f"Payment #{self.pk} - {self.status}"
