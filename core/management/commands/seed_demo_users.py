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

        self.stdout.write(self.style.SUCCESS(
            'Seeded demo users for all roles (admin/doctor/patient/'
            'lab/pharmacy/nurse/staff).'))
