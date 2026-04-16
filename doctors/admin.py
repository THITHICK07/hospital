from django.contrib import admin

from .models import Doctor, DoctorAvailability


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hospital_name', 'consultation_fee')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'time_slot', 'is_available')
    list_filter = ('is_available', 'date')
