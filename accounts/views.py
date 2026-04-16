from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from doctors.models import Doctor

from .forms import LoginForm, RegisterForm
from .models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        if self.request.user.role == User.DOCTOR:
            return reverse_lazy('appointments:doctor_appointments')
        if self.request.user.role == User.PATIENT:
            return reverse_lazy('appointments:patient_dashboard')
        return reverse_lazy('admin:index')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if user.role == User.DOCTOR:
            Doctor.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, 'Registration successful.')
        return redirect('core:dashboard_redirect')

    return render(request, 'accounts/register.html', {'form': form})
