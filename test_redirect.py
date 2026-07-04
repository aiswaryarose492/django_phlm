import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlm_project.settings')
django.setup()

from django.test import Client
from core.models import User, Patient, Doctor, Hospital

hospital = Hospital.objects.first()
doctor = Doctor.objects.first()

if not doctor:
    print("No doctor found")
    exit()

# Set up test user
user, _ = User.objects.get_or_create(username='testskip_user', defaults={'first_name': 'Test', 'email': 'testskip@example.com'})
user.set_password('password123')
user.save()

# Set up test patient
patient, _ = Patient.objects.get_or_create(user=user, defaults={'hospital': hospital, 'date_of_birth': '1990-01-01'})

client = Client()
client.login(username='testskip_user', password='password123')

print(f"Testing redirect for {user.username} (patient of {hospital.name}) to doctor {doctor.id}")
response = client.get(f'/book/{doctor.id}/details/')
print("Status code:", response.status_code)
if response.status_code == 302:
    print("Redirected to:", response.url)
else:
    print("Did not redirect! Check if user.is_authenticated and hasattr(user, 'patient_profile') are working.")
