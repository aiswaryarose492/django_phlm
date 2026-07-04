
import os
import django
import sys
from datetime import time

sys.path.append('d:\\phlm_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

from core.models import User, Doctor, Hospital

# 1. Setup Data
print("Setting up test data...")
try:
    hospital_user = User.objects.create_user(username='test_hospital_admin', password='password')
    hospital = Hospital.objects.create(user=hospital_user, name="Test Hospital", address="123 Test St")
    
    doc_user = User.objects.create_user(username='test_doctor', password='password', is_doctor=True)
    doctor = Doctor.objects.create(user=doc_user, hospital=hospital, specialty='General')
    
    print(f"Created Doctor: {doctor}")
except Exception as e:
    print(f"Setup failed (maybe already exists): {e}")
    # Try to fetch existing if failed
    hospital = Hospital.objects.first()
    doctor = Doctor.objects.first()

# 2. Check existence
print(f"Doctor count before soft delete: {Doctor.objects.filter(hospital=hospital).count()}")

# 3. Soft Delete
print("Soft deleting user (is_active=False)...")
doc_user = doctor.user
doc_user.is_active = False
doc_user.save()

# 4. Query again (The Bug)
count = Doctor.objects.filter(hospital=hospital).count()
print(f"Doctor count after soft delete (hospital query): {count}")

# Check Home Page Query behavior
home_query_count = Doctor.objects.filter(available=True, hospital=hospital).count()
print(f"Doctor count after soft delete (home page query available=True): {home_query_count}")

if count > 0 or home_query_count > 0:
    print("BUG REPRODUCED: Inactive doctor is still showing up in query!")
else:
    print("Bug not reproduced (Doctor not showing up).")

# 5. Correct Query (The Fix)
correct_count = Doctor.objects.filter(hospital=hospital, user__is_active=True).count()
print(f"Doctor count with correct filter: {correct_count}")

# Cleanup
print("Cleaning up...")
doc_user.delete()
hospital_user.delete()
