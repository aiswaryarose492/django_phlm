import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

from core.models import User, Hospital, Doctor, Patient, Staff, LabWorker, PharmacyWorker

def ensure_user_profiles():
    """Ensure all role users have their corresponding profiles and are active"""
    issues_fixed = []
    
    hospital = Hospital.objects.first()
    if not hospital:
        print("ERROR: No hospitals found in database. Create a hospital first.")
        return
    
    # Process doctors
    for user in User.objects.filter(is_doctor=True, is_active=True):
        if not hasattr(user, 'doctor_profile'):
            Doctor.objects.create(
                user=user,
                hospital=hospital,
                specialty='General',
                department='General Medicine',
                experience=0,
                available=True
            )
            issues_fixed.append(f"Created Doctor profile for {user.username}")
            print(f"Created Doctor profile for {user.username}")
    
    # Process patients
    for user in User.objects.filter(is_patient=True, is_active=True):
        if not hasattr(user, 'patient_profile'):
            Patient.objects.create(
                user=user,
                hospital=hospital,
                phone='',
                address=''
            )
            issues_fixed.append(f"Created Patient profile for {user.username}")
            print(f"Created Patient profile for {user.username}")
    
    # Process lab workers
    for user in User.objects.filter(is_lab=True, is_active=True):
        if not hasattr(user, 'lab_profile'):
            LabWorker.objects.create(
                user=user,
                hospital=hospital,
                phone=''
            )
            issues_fixed.append(f"Created LabWorker profile for {user.username}")
            print(f"Created LabWorker profile for {user.username}")
    
    # Process pharmacy workers
    for user in User.objects.filter(is_pharmacy=True, is_active=True):
        if not hasattr(user, 'pharmacy_profile'):
            PharmacyWorker.objects.create(
                user=user,
                hospital=hospital,
                phone=''
            )
            issues_fixed.append(f"Created PharmacyWorker profile for {user.username}")
            print(f"Created PharmacyWorker profile for {user.username}")
    
    # Process staff members
    for user in User.objects.filter(is_staff_member=True, is_active=True):
        if not hasattr(user, 'staff_profile'):
            Staff.objects.create(
                user=user,
                hospital=hospital,
                role='Other'
            )
            issues_fixed.append(f"Created Staff profile for {user.username}")
            print(f"Created Staff profile for {user.username}")
    
    # Ensure hospital admin users have hospital profile
    for user in User.objects.filter(is_hospital_admin=True, is_active=True):
        if not hasattr(user, 'hospital_profile'):
            Hospital.objects.create(
                user=user,
                name=f"{user.get_full_name() or user.username}'s Hospital",
                address=''
            )
            issues_fixed.append(f"Created Hospital profile for {user.username}")
            print(f"Created Hospital profile for {user.username}")
    
    if issues_fixed:
        print(f"\nFixed {len(issues_fixed)} issues.")
    else:
        print("\nAll user profiles are correctly configured.")

if __name__ == '__main__':
    ensure_user_profiles()