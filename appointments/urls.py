from django.urls import path

from .views import (
    AppointmentListApiView,
    book_appointment,
    cancel_appointment,
    complete_appointment,
    doctor_appointments,
    patient_dashboard,
    update_appointment_status,
)

app_name = 'appointments'

urlpatterns = [
    path('dashboard/', patient_dashboard, name='patient_dashboard'),
    path('book/<int:doctor_id>/', book_appointment, name='book_appointment'),
    path('cancel/<int:pk>/', cancel_appointment, name='cancel_appointment'),
    path('doctor/', doctor_appointments, name='doctor_appointments'),
    path('doctor/<int:pk>/complete/', complete_appointment, name='complete_appointment'),
    path('doctor/<int:pk>/<str:status>/', update_appointment_status, name='update_appointment_status'),
    path('api/appointments/', AppointmentListApiView.as_view(), name='appointment_api'),
]
