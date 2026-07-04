import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

from core.models import User, Doctor, Hospital

hospital = Hospital.objects.first()

user, created = User.objects.get_or_create(username='d1')
user.set_password('d')
user.is_doctor = True
user.save()

if not hasattr(user, 'doctor_profile'):
    Doctor.objects.create(
        user=user,
        hospital=hospital,
        specialty='General Medicine',
        department='General Medicine',
        experience=5,
        available=True
    )
    print("Doctor profile created")
else:
    print("Doctor profile already exists")

print("User d1 created/updated successfully")
