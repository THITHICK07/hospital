from django.urls import path

from .views import (
    DoctorListApiView,
    add_availability,
    delete_availability,
    doctor_dashboard,
    doctor_list_view,
    doctor_portal,
    doctor_profile_update,
    manage_slots,
)

app_name = 'doctors'

urlpatterns = [
    path('', doctor_list_view, name='doctor_list'),
    path('portal/', doctor_portal, name='doctor_portal'),
    path('dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('profile/', doctor_profile_update, name='doctor_profile'),
    path('slots/', manage_slots, name='manage_slots'),
    path('availability/add/', add_availability, name='add_availability'),
    path('availability/<int:pk>/delete/', delete_availability, name='delete_availability'),
    path('api/doctors/', DoctorListApiView.as_view(), name='doctor_api'),
]
