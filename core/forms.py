from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Hospital, Doctor, Patient, Appointment, LabReport, Reminder

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class DoctorForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    specialty = forms.CharField(max_length=100)

    class Meta:
        model = Doctor
        fields = ['specialty']

class PatientForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    age = forms.IntegerField()
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Patient
        fields = ['age', 'address']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'symptoms']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class LabReportForm(forms.ModelForm):
    class Meta:
        model = LabReport
        fields = ['patient', 'doctor', 'title', 'file']

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['type', 'message', 'time', 'is_active']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
