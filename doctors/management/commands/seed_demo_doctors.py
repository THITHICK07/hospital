import os
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from doctors.models import Doctor, DoctorAvailability, TIME_SLOT_CHOICES


SPECIALIST_DATA = {
    "Cardiology": [
        ("Aarav", "Sharma", "MD Cardiology", 12, Decimal("900.00")),
        ("Riya", "Kapoor", "DM Cardiology", 9, Decimal("850.00")),
        ("Vivaan", "Mehta", "MD Internal Medicine, Fellowship Cardiology", 11, Decimal("950.00")),
        ("Anaya", "Reddy", "DNB Cardiology", 8, Decimal("800.00")),
        ("Kabir", "Verma", "MD Cardiology", 14, Decimal("1000.00")),
    ],
    "Neurology": [
        ("Ishaan", "Nair", "DM Neurology", 13, Decimal("1100.00")),
        ("Diya", "Malhotra", "MD Neurology", 10, Decimal("950.00")),
        ("Arjun", "Bose", "DM Neurology", 7, Decimal("900.00")),
        ("Myra", "Sinha", "DNB Neurology", 8, Decimal("920.00")),
        ("Reyansh", "Kulkarni", "MD Neurology", 12, Decimal("1050.00")),
    ],
    "Orthopedics": [
        ("Aditya", "Rao", "MS Orthopedics", 15, Decimal("850.00")),
        ("Sara", "Joshi", "DNB Orthopedics", 9, Decimal("780.00")),
        ("Krish", "Patel", "MS Orthopedics", 11, Decimal("820.00")),
        ("Kiara", "Iyer", "Fellowship in Joint Replacement", 7, Decimal("800.00")),
        ("Yuvan", "Arora", "MS Trauma Care", 10, Decimal("830.00")),
    ],
    "Pediatrics": [
        ("Aadhya", "Gupta", "MD Pediatrics", 8, Decimal("700.00")),
        ("Vihaan", "Bhat", "DCH Pediatrics", 6, Decimal("650.00")),
        ("Siya", "Thomas", "MD Pediatrics", 11, Decimal("720.00")),
        ("Atharv", "Pillai", "DNB Pediatrics", 9, Decimal("680.00")),
        ("Navya", "Chopra", "MD Neonatology", 10, Decimal("760.00")),
    ],
    "Dermatology": [
        ("Pranav", "Singh", "MD Dermatology", 7, Decimal("750.00")),
        ("Meera", "Das", "DDVL Dermatology", 9, Decimal("800.00")),
        ("Dev", "Mishra", "MD Cosmetology", 6, Decimal("780.00")),
        ("Tara", "Khan", "MD Dermatology", 8, Decimal("790.00")),
        ("Ira", "Banerjee", "DDVL", 11, Decimal("850.00")),
    ],
    "Gynecology": [
        ("Saanvi", "Agarwal", "MS Obstetrics and Gynecology", 13, Decimal("900.00")),
        ("Pari", "Menon", "DGO Gynecology", 8, Decimal("820.00")),
        ("Aanya", "Saxena", "MS Gynecology", 12, Decimal("880.00")),
        ("Nitya", "Seth", "MD Reproductive Health", 9, Decimal("860.00")),
        ("Riddhi", "Jain", "MS Obstetrics", 7, Decimal("810.00")),
    ],
    "ENT": [
        ("Laksh", "Suri", "MS ENT", 10, Decimal("700.00")),
        ("Pihu", "Kaur", "DNB ENT", 8, Decimal("680.00")),
        ("Rudra", "Dutta", "MS ENT Surgery", 11, Decimal("740.00")),
        ("Avni", "Ghosh", "MS ENT", 7, Decimal("690.00")),
        ("Om", "Desai", "DNB ENT", 9, Decimal("720.00")),
    ],
}


class Command(BaseCommand):
    help = "Seed demo admin and specialist doctors using environment-based credentials."

    def handle(self, *args, **options):
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD")
        doctor_password = os.getenv("DEMO_DOCTOR_PASSWORD")
        demo_doctor_username = os.getenv("DEMO_DOCTOR_USERNAME", "doctor")

        if not admin_password or not doctor_password:
            self.stdout.write(self.style.ERROR("Set ADMIN_PASSWORD and DEMO_DOCTOR_PASSWORD in .env before seeding demo data."))
            return

        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": admin_email,
                "role": User.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "first_name": "System",
                "last_name": "Admin",
            },
        )
        admin_user.email = admin_email
        admin_user.role = User.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password(admin_password)
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_username}"))

        # Define slot values and start date before using them
        slot_values = [slot[0] for slot in TIME_SLOT_CHOICES[:4]]
        start_date = timezone.localdate() + timedelta(days=1)

        # Create demo doctor from environment variables
        demo_doctor_user, created = User.objects.get_or_create(
            username=demo_doctor_username,
            defaults={
                "email": f"{demo_doctor_username}@smarthealthcare.local",
                "role": User.DOCTOR,
                "first_name": "Demo",
                "last_name": "Doctor",
            },
        )
        demo_doctor_user.email = f"{demo_doctor_username}@smarthealthcare.local"
        demo_doctor_user.role = User.DOCTOR
        demo_doctor_user.first_name = "Demo"
        demo_doctor_user.last_name = "Doctor"
        demo_doctor_user.set_password(doctor_password)
        demo_doctor_user.save()
        
        demo_doctor, created = Doctor.objects.get_or_create(
            user=demo_doctor_user,
            defaults={
                "specialization": "General Physician",
                "qualification": "MBBS, MD General Medicine",
                "experience_years": 10,
                "consultation_fee": Decimal("500.00"),
                "phone": "+91-9000000001",
                "hospital_name": "Smart City Medical Center",
                "address": "Health Avenue, Central City",
                "bio": "Experienced general physician focused on comprehensive healthcare and patient wellness.",
            },
        )
        demo_doctor.specialization = "General Physician"
        demo_doctor.qualification = "MBBS, MD General Medicine"
        demo_doctor.experience_years = 10
        demo_doctor.consultation_fee = Decimal("500.00")
        demo_doctor.phone = "+91-9000000001"
        demo_doctor.hospital_name = "Smart City Medical Center"
        demo_doctor.address = "Health Avenue, Central City"
        demo_doctor.bio = "Experienced general physician focused on comprehensive healthcare and patient wellness."
        demo_doctor.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created demo doctor user: {demo_doctor_username}"))

        # Create availability slots for demo doctor
        for day_offset in range(5):
            appointment_date = start_date + timedelta(days=day_offset)
            for time_slot in slot_values:
                DoctorAvailability.objects.get_or_create(
                    doctor=demo_doctor,
                    date=appointment_date,
                    time_slot=time_slot,
                    defaults={"is_available": True},
                )

        created_count = 0
        for specialization, doctors in SPECIALIST_DATA.items():
            for index, (first_name, last_name, qualification, experience, fee) in enumerate(doctors, start=1):
                username = f"{specialization.lower().replace(' ', '')}{index}"
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": f"{username}@smarthealthcare.local",
                        "role": User.DOCTOR,
                    },
                )
                user.first_name = first_name
                user.last_name = last_name
                user.email = f"{username}@smarthealthcare.local"
                user.role = User.DOCTOR
                user.set_password(doctor_password)
                user.save()

                doctor, doctor_created = Doctor.objects.get_or_create(
                    user=user,
                    defaults={
                        "specialization": specialization,
                        "qualification": qualification,
                        "experience_years": experience,
                        "consultation_fee": fee,
                        "phone": f"+91-90000{index:05d}",
                        "hospital_name": "Smart City Medical Center",
                        "address": "Health Avenue, Central City",
                        "bio": f"Experienced {specialization.lower()} specialist focused on patient-friendly diagnosis and guided treatment plans.",
                    },
                )
                doctor.specialization = specialization
                doctor.qualification = qualification
                doctor.experience_years = experience
                doctor.consultation_fee = fee
                doctor.phone = f"+91-90000{index:05d}"
                doctor.hospital_name = "Smart City Medical Center"
                doctor.address = "Health Avenue, Central City"
                doctor.bio = f"Experienced {specialization.lower()} specialist focused on patient-friendly diagnosis and guided treatment plans."
                doctor.save()

                for day_offset in range(5):
                    appointment_date = start_date + timedelta(days=day_offset)
                    for time_slot in slot_values:
                        DoctorAvailability.objects.get_or_create(
                            doctor=doctor,
                            date=appointment_date,
                            time_slot=time_slot,
                            defaults={"is_available": True},
                        )

                if doctor_created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Demo seed complete. Doctors available: {Doctor.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"New doctor profiles created in this run: {created_count}"))
