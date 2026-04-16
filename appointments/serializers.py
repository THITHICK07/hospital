from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient_name',
            'doctor_name',
            'date',
            'time_slot',
            'status',
            'reason',
        ]
    
    def get_doctor_name(self, obj):
        if obj.doctor:
            return obj.doctor.user.get_full_name()
        return 'No Doctor Assigned'
