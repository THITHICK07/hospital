from django.shortcuts import redirect, render

from accounts.models import User
from appointments.models import Appointment
from doctors.models import Doctor


def home_view(request):
    featured_doctors = Doctor.objects.select_related('user').exclude(specialization='')[:6]
    specialization_count = (
        Doctor.objects.exclude(specialization='')
        .values('specialization')
        .distinct()
        .count()
    )
    return render(
        request,
        'core/home.html',
        {
            'doctor_count': Doctor.objects.count(),
            'appointment_count': Appointment.objects.count(),
            'featured_doctors': featured_doctors,
            'specialization_count': specialization_count,
        },
    )


def dashboard_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('core:home')
    if request.user.role == User.DOCTOR:
        return redirect('doctors:doctor_dashboard')
    if request.user.role == User.PATIENT:
        return redirect('appointments:patient_dashboard')
    return redirect('admin:index')
