from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import Patient, User
from doctors.models import Doctor, DoctorAvailability

from .models import Appointment


class AppointmentFlowTests(TestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            role=User.PATIENT,
            first_name='Pat',
            last_name='Ient',
        )
        self.patient = Patient.objects.create(user=self.patient_user)

        self.doctor_user = User.objects.create_user(
            username='doctor1',
            password='testpass123',
            role=User.DOCTOR,
            first_name='Sam',
            last_name='Doctor',
        )
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialization='Cardiology')

        self.other_doctor_user = User.objects.create_user(
            username='doctor2',
            password='testpass123',
            role=User.DOCTOR,
            first_name='Alex',
            last_name='Other',
        )
        self.other_doctor = Doctor.objects.create(user=self.other_doctor_user, specialization='Neurology')

        appointment_date = date.today() + timedelta(days=1)
        self.time_slot = '09:00 AM - 10:00 AM'

        DoctorAvailability.objects.create(
            doctor=self.doctor,
            date=appointment_date,
            time_slot=self.time_slot,
            is_available=False,
        )
        DoctorAvailability.objects.create(
            doctor=self.other_doctor,
            date=appointment_date,
            time_slot=self.time_slot,
            is_available=False,
        )

        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=appointment_date,
            time_slot=self.time_slot,
            specialization=self.doctor.specialization,
            status=Appointment.APPROVED,
        )
        self.other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.other_doctor,
            date=appointment_date,
            time_slot=self.time_slot,
            specialization=self.other_doctor.specialization,
            status=Appointment.APPROVED,
        )

    def test_doctor_appointments_show_shared_records_for_all_doctors(self):
        self.client.login(username='doctor1', password='testpass123')

        response = self.client.get(reverse('appointments:doctor_appointments'))

        self.assertEqual(response.status_code, 200)
        appointments = list(response.context['appointments'])
        self.assertIn(self.appointment, appointments)
        self.assertIn(self.other_appointment, appointments)

    def test_doctor_appointments_can_filter_by_specialization(self):
        self.client.login(username='doctor1', password='testpass123')

        response = self.client.get(reverse('appointments:doctor_appointments'), {'specialization': 'Cardiology'})

        self.assertEqual(response.status_code, 200)
        appointments = list(response.context['appointments'])
        self.assertIn(self.appointment, appointments)
        self.assertNotIn(self.other_appointment, appointments)

    def test_completing_appointment_updates_status_and_patient_history(self):
        self.client.login(username='doctor1', password='testpass123')

        response = self.client.get(reverse('appointments:complete_appointment', args=[self.other_appointment.pk]))

        self.assertRedirects(response, reverse('appointments:doctor_appointments'))
        self.other_appointment.refresh_from_db()
        self.assertEqual(self.other_appointment.status, Appointment.COMPLETED)
        self.assertTrue(
            DoctorAvailability.objects.get(
                doctor=self.other_doctor,
                date=self.other_appointment.date,
                time_slot=self.other_appointment.time_slot,
            ).is_available
        )

        response = self.client.get(reverse('appointments:doctor_appointments'))
        self.assertIn(self.other_appointment, list(response.context['completed_appointments']))

        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(reverse('appointments:patient_dashboard'))
        self.assertContains(response, 'Completed')
        self.assertContains(response, self.other_appointment.time_slot)
