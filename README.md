# Smart Healthcare Appointment System

College-level Django project for doctor appointment booking, doctor schedule management, and simple mock payments.

## Features

- Custom user model with patient, doctor, and admin roles
- Patient registration, login, doctor browsing, appointment booking, cancellation, and history
- Doctor profile management, availability slot creation, appointment approval and rejection
- Admin panel management for users, doctors, appointments, and payments
- Basic DRF APIs for doctors and appointments
- PostgreSQL environment configuration with Render-ready deployment setup

## Project Structure

- `accounts` - authentication, custom user, patient profile
- `doctors` - doctor profile, availability slots, doctor listing, doctor API
- `appointments` - booking flow, dashboards, appointment management, appointment API
- `payments` - mock payment tracking
- `core` - homepage and dashboard redirection

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update PostgreSQL credentials.
4. Run migrations:
   `python manage.py makemigrations`
   `python manage.py migrate`
5. Create a superuser:
   `python manage.py createsuperuser`
6. Start the development server:
   `python manage.py runserver`

## Demo Seed

- Put `ADMIN_PASSWORD` and `DEMO_DOCTOR_PASSWORD` inside `.env`
- Run:
  `python manage.py seed_demo_doctors`
- This creates:
  - 1 admin user from environment values
  - 7 specialist departments
  - 5 doctors per department
  - availability slots for upcoming days

## API Endpoints

- `/doctors/api/doctors/`
- `/appointments/api/appointments/`

## Render Deployment

- Add environment variables from `.env.example`
- Set build command:
  `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Set start command:
  `gunicorn myproject.wsgi`
