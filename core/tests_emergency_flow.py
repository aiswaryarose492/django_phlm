from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Hospital, Doctor, Staff, LabWorker, EmergencyCase, StaffHealthStatus, WorkLog
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class EmergencyFlowTest(TestCase):
    def setUp(self):
        # Setup Admin
        self.admin_user = User.objects.create_user(username='admin', password='password', is_hospital_admin=True)
        
        # Setup Hospital
        self.hospital = Hospital.objects.create(user=self.admin_user, name="Citadel Hospital", address="123 Citadel")
        
        # Setup Doctor
        self.doc_user = User.objects.create_user(username='doctor', password='password', is_doctor=True)
        Doctor.objects.create(user=self.doc_user, hospital=self.hospital, specialty="General")
        
        # Setup Staff (Nurse)
        self.staff_user = User.objects.create_user(username='nurse', password='password', is_staff_member=True)
        Staff.objects.create(user=self.staff_user, hospital=self.hospital, role="Nurse")
        
        self.client = Client()

    def test_emergency_case_creation(self):
        self.client.login(username='admin', password='password')
        response = self.client.post('/emergency/create/', {
            'patient_name': 'John Doe',
            'symptoms': 'Severe Chest Pain',
            'severity': 'Critical',
            'assigned_to': self.doc_user.id
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EmergencyCase.objects.filter(patient_name='John Doe').exists())
        case = EmergencyCase.objects.get(patient_name='John Doe')
        self.assertEqual(case.assigned_to, self.doc_user)

    def test_doctor_sees_emergency(self):
        # Create case assigned to doctor
        case = EmergencyCase.objects.create(
            hospital=self.hospital,
            patient_name="Jane Doe",
            symptoms="Flu",
            severity="Moderate",
            assigned_to=self.doc_user
        )
        
        self.client.login(username='doctor', password='password')
        response = self.client.get('/doctor/')
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "Flu")
        self.assertContains(response, "Emergency Assignments")

    def test_staff_wellbeing_flow(self):
        self.client.login(username='nurse', password='password')
        
        # Access Dashboard
        response = self.client.get('/staff_dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Toggle Shift (Start)
        response = self.client.get('/staff/toggle-shift/', follow=True)
        self.assertContains(response, "On Duty")
        
        status = StaffHealthStatus.objects.get(worker=self.staff_user, date=timezone.now().date())
        self.assertTrue(status.is_on_duty)
        self.assertIsNotNone(status.shift_start)
        
        # Update Water
        response = self.client.get('/staff/update-water/', follow=True)
        status.refresh_from_db()
        self.assertEqual(status.water_intake, 1)
        
        # Toggle Shift (End)
        response = self.client.get('/staff/toggle-shift/', follow=True)
        status.refresh_from_db()
        self.assertFalse(status.is_on_duty)

    def test_hospital_monitor_sees_active_staff(self):
        # Nurse goes on duty
        StaffHealthStatus.objects.create(
            worker=self.staff_user, 
            date=timezone.now().date(),
            is_on_duty=True,
            shift_start=timezone.now() - timedelta(hours=2)
        )
        
        self.client.login(username='admin', password='password')
        response = self.client.get('/hospital/')
        self.assertContains(response, "On Duty")
        self.assertContains(response, "2.0 hrs")
