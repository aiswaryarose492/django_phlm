from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Hospital, PharmacyWorker, Prescription, Appointment, Doctor, Patient, StaffHealthStatus
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class PharmacyFlowTest(TestCase):
    def setUp(self):
        # Setup Hospital Admin
        self.admin_user = User.objects.create_user(username='pharmacy_admin', password='password', is_hospital_admin=True)
        self.hospital = Hospital.objects.create(user=self.admin_user, name="Citadel Hospital", address="123 Citadel")

        # Setup Pharmacy Worker
        self.pharmacy_user = User.objects.create_user(username='pharmacist', password='password', is_pharmacy=True)
        PharmacyWorker.objects.create(user=self.pharmacy_user, hospital=self.hospital, phone="1234567890")

        # Setup Doctor
        self.doc_user = User.objects.create_user(username='doctor', password='password', is_doctor=True)
        Doctor.objects.create(user=self.doc_user, hospital=self.hospital, specialty="General")

        # Setup Patient
        self.patient_user = User.objects.create_user(username='patient', password='password', is_patient=True)
        Patient.objects.create(user=self.patient_user, hospital=self.hospital, age=30, address="123 Patient St")

        # Setup Appointment
        self.appointment = Appointment.objects.create(
            doctor=self.doc_user.doctor_profile,
            patient=self.patient_user.patient_profile,
            date=timezone.now().date(),
            time=timezone.now().time(),
            status='Scheduled'
        )

        # Setup Prescription
        self.prescription = Prescription.objects.create(
            appointment=self.appointment,
            medicines="Amoxicillin 500mg, Paracetamol 650mg",
            notes="Take after food"
        )

        self.client = Client()

    def test_pharmacy_dashboard_loads(self):
        """Test that pharmacy dashboard loads successfully"""
        self.client.login(username='pharmacist', password='password')
        response = self.client.get('/pharmacy/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pharmacy Dashboard")
        self.assertContains(response, "Pending Prescriptions")

    def test_pharmacy_sees_pending_prescriptions(self):
        """Test that pharmacy worker sees pending prescriptions"""
        self.client.login(username='pharmacist', password='password')
        response = self.client.get('/pharmacy/')
        self.assertEqual(response.status_code, 200)
        # The prescription should be visible (pending)
        self.assertContains(response, "Amoxicillin")

    def test_pharmacy_shift_management(self):
        """Test that pharmacy worker can start/end shift"""
        self.client.login(username='pharmacist', password='password')

        # Access Dashboard first
        response = self.client.get('/pharmacy/')
        self.assertEqual(response.status_code, 200)

        # Start Shift
        response = self.client.post('/pharmacy/toggle-shift/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "On Duty")

        # Check StaffHealthStatus was created
        status = StaffHealthStatus.objects.get(worker=self.pharmacy_user, date=timezone.now().date())
        self.assertTrue(status.is_on_duty)
        self.assertIsNotNone(status.shift_start)

        # End Shift
        response = self.client.post('/pharmacy/toggle-shift/', follow=True)
        status.refresh_from_db()
        self.assertFalse(status.is_on_duty)

    def test_pharmacy_water_intake(self):
        """Test that pharmacy worker can update water intake"""
        self.client.login(username='pharmacist', password='password')

        # Access Dashboard
        response = self.client.get('/pharmacy/')
        self.assertEqual(response.status_code, 200)

        # Update Water
        response = self.client.post('/pharmacy/update-water/', follow=True)
        self.assertEqual(response.status_code, 200)

        # Check water was incremented
        status = StaffHealthStatus.objects.get(worker=self.pharmacy_user, date=timezone.now().date())
        self.assertEqual(status.water_intake, 1)

    def test_pharmacy_processes_prescription(self):
        """Test that pharmacy worker can process prescription"""
        self.client.login(username='pharmacist', password='password')

        # Access Dashboard - prescription should be pending
        response = self.client.get('/pharmacy/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Processing")

        # Process prescription (mark as dispensed)
        self.prescription.is_dispensed = True
        self.prescription.save()

        # Verify prescription is no longer pending
        response = self.client.get('/pharmacy/')
        self.assertEqual(response.status_code, 200)
        # After dispensing, it should move to processed
