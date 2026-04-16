from django.apps import AppConfig
import os


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # 🔹 Admin details from ENV
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        # 🔹 Doctor details from ENV
        doctor_username = os.getenv("DEMO_DOCTOR_USERNAME", "doctor")
        doctor_password = os.getenv("DEMO_DOCTOR_PASSWORD", "doctor123")

        # ✅ Create ADMIN if not exists
        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            print("✅ Admin user created")

        # ✅ Create DOCTOR if not exists
        if not User.objects.filter(username=doctor_username).exists():
            User.objects.create_user(
                username=doctor_username,
                password=doctor_password
            )
            print("✅ Doctor user created")