from django.contrib import admin
from django.urls import include, path

from appointments.views import AppointmentListApiView
from doctors.views import DoctorListApiView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('payments/', include('payments.urls')),
    path('api/doctors/', DoctorListApiView.as_view(), name='api_doctors'),
    path('api/appointments/', AppointmentListApiView.as_view(), name='api_appointments'),
]
