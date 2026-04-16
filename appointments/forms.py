from django import forms

from doctors.models import DoctorAvailability, TIME_SLOT_CHOICES

from .models import Appointment


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time_slot', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}, choices=TIME_SLOT_CHOICES),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')
        if self.doctor and date and time_slot:
            exists = DoctorAvailability.objects.filter(
                doctor=self.doctor,
                date=date,
                time_slot=time_slot,
                is_available=True,
            ).exists()
            if not exists:
                raise forms.ValidationError('Selected slot is not available.')
        return cleaned_data
