"""Seed demo users for every role so the Flutter login-screen demo
chips (admin/admin123, doctor1/doctor123, patient1/patient123,
lab1/lab123, pharm1/pharm123, nurse1/nurse123, staff1/staff123)
log in against the LIVE Django backend, not just offline seed data.

Idempotent: safe to run multiple times.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core import models

U = get_user_model()


def make_user(username, password, **flags):
    u, created = U.objects.get_or_create(username=username, defaults=flags)
    if not created:
        for k, v in flags.items():
            setattr(u, k, v)
    u.set_password(password)
    u.save()
    return u


class Command(BaseCommand):
    help = 'Create demo users for every role (admin/doctor/patient/lab/pharmacy/nurse/staff).'

    def handle(self, *args, **opts):
        # 1. Create Hospital Admin user first
        admin = make_user(
            'admin', 'admin123',
            is_hospital_admin=True, is_staff=True,
            first_name='Hospital', last_name='Admin',
            email='admin@phlm.local',
        )

        # 2. Get or create the Hospital linked to the admin user
        hospital, _ = models.Hospital.objects.get_or_create(
            user=admin,
            defaults={
                'name': 'AZEEZIA HOSPITAL',
                'address': 'Demo Hospital Road, Kerala',
                'max_leave_days': 12,
                'extra_leave_deduction': 0.0,
            }
        )

        # Doctor
        doc = make_user(
            'doctor1', 'doctor123',
            is_doctor=True, first_name='Demo', last_name='Doctor',
            email='doctor1@phlm.local',
        )
        models.Doctor.objects.get_or_create(
            user=doc, hospital=hospital,
            defaults={
                'specialty': 'General Medicine', 'department': 'General Medicine',
                'qualification': 'MBBS', 'experience': 8, 'available': True,
                'appointment_fees': 250.0,
            },
        )

        # Patient
        pat = make_user(
            'patient1', 'patient123',
            is_patient=True, first_name='Demo', last_name='Patient',
            email='patient1@phlm.local',
        )
        models.Patient.objects.get_or_create(
            user=pat, hospital=hospital,
            defaults={'phone': '9999990001', 'gender': 'Male',
                     'water_goal': 8},
        )

        # Lab
        lab = make_user(
            'lab1', 'lab123',
            is_lab=True, first_name='Demo', last_name='Lab',
            email='lab1@phlm.local',
        )
        models.LabWorker.objects.get_or_create(
            user=lab, hospital=hospital, defaults={'phone': '9999990002'})

        # Pharmacy
        pharm = make_user(
            'pharm1', 'pharm123',
            is_pharmacy=True, first_name='Demo', last_name='Pharmacy',
            email='pharm1@phlm.local',
        )
        models.PharmacyWorker.objects.get_or_create(
            user=pharm, hospital=hospital, defaults={'phone': '9999990003'})

        # Nurse (staff, role Nurse)
        nurse = make_user(
            'nurse1', 'nurse123',
            is_staff_member=True, first_name='Demo', last_name='Nurse',
            email='nurse1@phlm.local',
        )
        models.Staff.objects.get_or_create(
            user=nurse, hospital=hospital,
            defaults={'role': 'Nurse', 'phone': '9999990004'})

        # Other Staff
        staff = make_user(
            'staff1', 'staff123',
            is_staff_member=True, first_name='Demo', last_name='Staff',
            email='staff1@phlm.local',
        )
        models.Staff.objects.get_or_create(
            user=staff, hospital=hospital,
            defaults={'role': 'Other', 'phone': '9999990005'})

        # ---- STAGE 3: Test Accounts for API Testing (as per user requests) ----
        # 1. Superuser
        make_user('test_superuser', 'SuperuserPass123!', is_superuser=True, is_staff=True, email='test_superuser@phlm.local')

        # 2. Hospital Admin
        h_admin = make_user('test_hospital_admin', 'HospitalAdminPass123!', is_hospital_admin=True, email='test_hospital_admin@phlm.local')
        models.Hospital.objects.get_or_create(
            user=h_admin,
            defaults={
                'name': 'Test Hospital',
                'address': '123 Test St',
                'max_leave_days': 12,
                'extra_leave_deduction': 0.0
            }
        )

        # 3. Doctor (test_doctor with DoctorTestPass123!)
        t_doc = make_user('test_doctor', 'DoctorTestPass123!', is_doctor=True, email='test_doctor@phlm.local')
        models.Doctor.objects.get_or_create(
            user=t_doc, hospital=hospital,
            defaults={
                'specialty': 'General Medicine', 'department': 'General Medicine',
                'experience': 5, 'available': True
            }
        )

        # 4. Patient
        t_pat = make_user('test_patient', 'PatientPass123!', is_patient=True, email='test_patient@phlm.local')
        models.Patient.objects.get_or_create(user=t_pat, hospital=hospital, defaults={'phone': '1234567890'})

        # 5. Lab Worker
        t_lab = make_user('test_lab', 'LabPass123!', is_lab=True, email='test_lab@phlm.local')
        models.LabWorker.objects.get_or_create(user=t_lab, hospital=hospital, defaults={'phone': '1234567890'})

        # 6. Pharmacy Worker
        t_pharm = make_user('test_pharmacy', 'PharmacyPass123!', is_pharmacy=True, email='test_pharmacy@phlm.local')
        models.PharmacyWorker.objects.get_or_create(user=t_pharm, hospital=hospital, defaults={'phone': '1234567890'})

        # 7. Nurse
        t_nurse = make_user('test_nurse', 'NursePass123!', is_staff_member=True, email='test_nurse@phlm.local')
        models.Staff.objects.get_or_create(user=t_nurse, hospital=hospital, defaults={'role': 'Nurse', 'phone': '1234567890'})

        # 8. Other Staff
        t_staff = make_user('test_other_staff', 'OtherStaffPass123!', is_staff_member=True, email='test_other_staff@phlm.local')
        models.Staff.objects.get_or_create(user=t_staff, hospital=hospital, defaults={'role': 'Other', 'phone': '1234567890'})

        self.stdout.write(self.style.SUCCESS(
            'Seeded demo and test users for all roles successfully.'))
