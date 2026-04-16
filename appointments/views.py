from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.generics import ListAPIView

from accounts.decorators import role_required
from accounts.models import Patient
from doctors.models import Doctor, DoctorAvailability
from payments.models import Payment

from .forms import AppointmentBookingForm
from .models import Appointment
from .serializers import AppointmentSerializer


@login_required
@role_required('patient')
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user').order_by('-date', '-created_at')
    payments = Payment.objects.filter(appointment__patient=patient).select_related('appointment__doctor__user')
    return render(
        request,
        'appointments/patient_dashboard.html',
        {
            'history': appointments,
            'payments': payments[:5],
            'stats': {
                'total': appointments.count(),
                'approved': appointments.filter(status=Appointment.APPROVED).count(),
                'pending': appointments.filter(status=Appointment.PENDING).count(),
            },
        },
    )


@login_required
@role_required('patient')
def book_appointment(request, doctor_id):
    patient = get_object_or_404(Patient, user=request.user)
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    form = AppointmentBookingForm(request.POST or None, doctor=doctor)
    # Show all slots, both available and booked
    all_slots = DoctorAvailability.objects.filter(doctor=doctor).order_by('date', 'time_slot')
    available_slots = all_slots.filter(is_available=True)

    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = patient
        appointment.doctor = doctor
        appointment.specialization = doctor.specialization
        appointment.status = Appointment.APPROVED
        appointment.full_clean()
        appointment.save()

        availability = get_object_or_404(
            DoctorAvailability,
            doctor=doctor,
            date=appointment.date,
            time_slot=appointment.time_slot,
            is_available=True,
        )
        availability.is_available = False
        availability.save(update_fields=['is_available'])

        Payment.objects.get_or_create(
            appointment=appointment,
            defaults={'amount': doctor.consultation_fee, 'status': Payment.PENDING},
        )
        messages.success(request, 'Appointment booked successfully.')
        return redirect('appointments:patient_dashboard')

    return render(
        request,
        'appointments/book_appointment.html',
        {'form': form, 'doctor': doctor, 'available_slots': available_slots, 'all_slots': all_slots},
    )


@login_required
@role_required('patient')
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient__user=request.user)
    if appointment.status != Appointment.CANCELLED:
        appointment.status = Appointment.CANCELLED
        appointment.save(update_fields=['status'])
        DoctorAvailability.objects.filter(
            doctor=appointment.doctor,
            date=appointment.date,
            time_slot=appointment.time_slot,
        ).update(is_available=True)
        messages.success(request, 'Appointment cancelled.')
    return redirect('appointments:patient_dashboard')


@login_required
@role_required('doctor')
def doctor_appointments(request):
    all_appointments = Appointment.objects.select_related('patient__user', 'doctor__user').order_by('date', 'time_slot')
    
    # Get all specializations
    specializations = Doctor.objects.exclude(specialization='').values_list('specialization', flat=True).distinct()
    selected_specialization = request.GET.get('specialization', 'all')
    
    # Filter by specialization if selected
    if selected_specialization and selected_specialization != 'all':
        all_appointments = all_appointments.filter(specialization=selected_specialization)
    
    # Show pending and approved appointments in main view
    appointments = all_appointments.exclude(status=Appointment.CANCELLED).exclude(status=Appointment.COMPLETED)
    
    # Show completed appointments in history
    completed_appointments = all_appointments.filter(status=Appointment.COMPLETED)
    
    context = {
        'appointments': appointments,
        'completed_appointments': completed_appointments,
        'specializations': specializations,
        'selected_specialization': selected_specialization,
    }
    
    return render(request, 'appointments/doctor_appointments.html', context)


@login_required
@role_required('doctor')
def update_appointment_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk, doctor__user=request.user)
    if status == 'approve':
        appointment.status = Appointment.APPROVED
        messages.success(request, 'Appointment approved.')
    else:
        appointment.status = Appointment.CANCELLED
        DoctorAvailability.objects.filter(
            doctor=appointment.doctor,
            date=appointment.date,
            time_slot=appointment.time_slot,
        ).update(is_available=True)
        messages.success(request, 'Appointment rejected.')
    appointment.save(update_fields=['status'])
    return redirect('appointments:doctor_appointments')


@login_required
@role_required('doctor')
def complete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status != Appointment.COMPLETED and appointment.status != Appointment.CANCELLED:
        appointment.status = Appointment.COMPLETED
        appointment.save(update_fields=['status'])
        
        # Make the slot available again
        DoctorAvailability.objects.filter(
            doctor=appointment.doctor,
            date=appointment.date,
            time_slot=appointment.time_slot,
        ).update(is_available=True)
        
        messages.success(request, 'Appointment marked as complete.')
    return redirect('appointments:doctor_appointments')


class AppointmentListApiView(ListAPIView):
    queryset = Appointment.objects.select_related('patient__user', 'doctor__user').all()
    serializer_class = AppointmentSerializer
