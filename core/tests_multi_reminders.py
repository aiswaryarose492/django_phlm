from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Patient, Reminder, Hospital, Doctor, Appointment, Prescription

class MultipleRemindersTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital_user = User.objects.create_user(username='hospital_admin', password='password123', is_hospital_admin=True)
        self.hospital = Hospital.objects.create(user=self.hospital_user, name="Test Hospital", address="Test Address")
        
        self.doctor_user = User.objects.create_user(username='doctor1', password='password123', is_doctor=True)
        self.doctor = Doctor.objects.create(user=self.doctor_user, hospital=self.hospital, specialty="General")
        
        self.patient_user = User.objects.create_user(username='patient1', password='password123', is_patient=True)
        self.patient = Patient.objects.create(user=self.patient_user, hospital=self.hospital)
        
        self.pharmacy_user = User.objects.create_user(username='pharma1', password='password123', is_pharmacy=True)
        from .models import PharmacyWorker
        PharmacyWorker.objects.create(user=self.pharmacy_user, hospital=self.hospital)
        
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=timezone.now().date(),
            time='10:00',
            symptoms='Fever',
            status='Completed'
        )
        self.prescription = Prescription.objects.create(
            appointment=self.appointment,
            medicines='Paracetamol, Amoxicillin',
            notes='Take care'
        )

    def test_process_multiple_medicines(self):
        self.client.force_login(self.pharmacy_user)
        url = reverse('process_prescription', args=[self.prescription.id])
        
        data = {
            'medicine_name[]': ['Meds A', 'Meds B'],
            'time[]': ['08:00', '20:00'],
            'instruction[]': ['Before Food', 'After Food']
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify Reminders
        reminders = Reminder.objects.filter(patient=self.patient)
        self.assertEqual(reminders.count(), 2)
        
        r1 = reminders.filter(message__contains='Meds A').first()
        self.assertIsNotNone(r1)
        self.assertEqual(str(r1.time), '08:00:00')
        
        r2 = reminders.filter(message__contains='Meds B').first()
        self.assertIsNotNone(r2)
        self.assertEqual(str(r2.time), '20:00:00')
        
        # Verify Prescription Status
        self.prescription.refresh_from_db()
        self.assertTrue(self.prescription.is_dispensed)
