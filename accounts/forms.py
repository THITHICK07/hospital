from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Patient, User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=150,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
    )
    current_medications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List any medications you are currently taking'}),
        label='Current Medications',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.PATIENT
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            patient, created = Patient.objects.get_or_create(user=user)
            if self.cleaned_data.get('age'):
                patient.age = self.cleaned_data['age']
            if self.cleaned_data.get('current_medications'):
                patient.current_medications = self.cleaned_data['current_medications']
            patient.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
