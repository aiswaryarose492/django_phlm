
import os
import django
import sys

# Add project root to path
sys.path.append('d:\\phlm_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlm_project.settings')
django.setup()

from core.models import User, Doctor, Staff, Patient

print("--- Users ---")
for u in User.objects.all():
    print(f"User: {u.username}, Active: {u.is_active}, ID: {u.id}")

print("\n--- Doctors ---")
for d in Doctor.objects.all():
    print(f"Doctor: {d.user.username}, User Active: {d.user.is_active}")

print("\n--- Staff ---")
for s in Staff.objects.all():
    print(f"Staff: {s.user.username}, User Active: {s.user.is_active}")

print("\n--- Patients ---")
for p in Patient.objects.all():
    print(f"Patient: {p.user.username}, User Active: {p.user.is_active}")
