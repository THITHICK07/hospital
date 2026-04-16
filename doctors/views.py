from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.generics import ListAPIView

from accounts.decorators import role_required
from accounts.models import User
from appointments.models import Appointment

from .forms import DoctorAvailabilityForm, DoctorProfileForm
from .models import Doctor, DoctorAvailability
from .serializers import DoctorSerializer


def doctor_portal(request):
    """Common page for all doctors to access their portal"""
    if request.user.is_authenticated and request.user.role == User.DOCTOR:
        return redirect('doctors:doctor_dashboard')
    return render(request, 'doctors/doctor_portal.html')


def doctor_list_view(request):
    specialization = request.GET.get('specialization', '')
    doctors = Doctor.objects.select_related('user').all().order_by('specialization', 'user__first_name')
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    specializations = Doctor.objects.exclude(specialization='').values_list('specialization', flat=True).distinct()
    return render(
        request,
        'doctors/doctor_list.html',
        {
            'doctors': doctors,
            'specializations': specializations,
            'selected_specialization': specialization,
        },
    )


@login_required
@role_required('doctor')
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user').order_by('date', 'time_slot')
    availabilities = doctor.availabilities.all()[:10]
    availability_form = DoctorAvailabilityForm()
    stats = {
        'total': appointments.count(),
        'pending': appointments.filter(status=Appointment.PENDING).count(),
        'approved': appointments.filter(status=Appointment.APPROVED).count(),
    }
    return render(
        request,
        'doctors/doctor_dashboard.html',
        {
            'doctor': doctor,
            'appointments': appointments[:8],
            'availabilities': availabilities,
            'availability_form': availability_form,
            'stats': stats,
        },
    )


@login_required
@role_required('doctor')
def doctor_profile_update(request):
    doctor, _ = Doctor.objects.get_or_create(user=request.user)
    form = DoctorProfileForm(request.POST or None, instance=doctor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('doctors:doctor_dashboard')
    return render(request, 'doctors/doctor_profile_form.html', {'form': form})


@login_required
@role_required('doctor')
def add_availability(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    form = DoctorAvailabilityForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        availability = form.save(commit=False)
        availability.doctor = doctor
        try:
            availability.save()
            messages.success(request, 'Availability slot added.')
        except IntegrityError:
            messages.error(request, 'This time slot already exists.')
    return redirect('doctors:doctor_dashboard')


@login_required
@role_required('doctor')
def delete_availability(request, pk):
    availability = get_object_or_404(DoctorAvailability, pk=pk, doctor__user=request.user)
    if not availability.is_available:
        messages.error(request, 'Booked slots cannot be deleted.')
    else:
        availability.delete()
        messages.success(request, 'Availability removed.')
    return redirect('doctors:doctor_dashboard')


@login_required
@role_required('doctor')
def manage_slots(request):
    """Manage doctor availability slots"""
    doctor = get_object_or_404(Doctor, user=request.user)
    
    # Get all specializations for dropdown
    specializations = Doctor.objects.exclude(specialization='').values_list('specialization', flat=True).distinct()
    
    # Get doctors by selected specialization
    selected_specialization = request.GET.get('specialization', '')
    selected_doctor_id = request.GET.get('doctor', '')
    
    if selected_specialization:
        doctors_in_spec = Doctor.objects.filter(specialization=selected_specialization).select_related('user')
    else:
        doctors_in_spec = []
    
    # Get slots for selected doctor (default to logged-in doctor)
    if selected_doctor_id:
        try:
            selected_doctor = Doctor.objects.get(id=selected_doctor_id, user__role='doctor')
        except Doctor.DoesNotExist:
            selected_doctor = doctor
    else:
        selected_doctor = doctor
    
    slots = selected_doctor.availabilities.all().order_by('date', 'time_slot')
    form = DoctorAvailabilityForm()
    
    if request.method == 'POST' and form.is_valid():
        availability = form.save(commit=False)
        availability.doctor = selected_doctor
        try:
            availability.save()
            messages.success(request, 'Slot added successfully.')
            return redirect(f'?specialization={selected_doctor.specialization}&doctor={selected_doctor.id}')
        except IntegrityError:
            messages.error(request, 'This slot already exists.')
    
    return render(request, 'doctors/manage_slots.html', {
        'doctor': doctor,
        'selected_doctor': selected_doctor,
        'specializations': specializations,
        'doctors_in_spec': doctors_in_spec,
        'selected_specialization': selected_specialization,
        'selected_doctor_id': selected_doctor_id,
        'slots': slots,
        'form': form,
    })


class DoctorListApiView(ListAPIView):
    queryset = Doctor.objects.select_related('user').all()
    serializer_class = DoctorSerializer
