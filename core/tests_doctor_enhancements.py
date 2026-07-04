
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Hospital, Doctor, EmergencyCase, StaffHealthStatus, WorkLog
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

class DoctorEnhancementsTest(TestCase):
    def setUp(self):
        # Setup Hospital & Admin
        self.admin = User.objects.create_user(username='admin', password='password', is_hospital_admin=True)
        self.hospital = Hospital.objects.create(user=self.admin, name="Test Hospital", address="123 Test St")
        
        # Setup Doctor
        self.doctor_user = User.objects.create_user(username='doctor', password='password', is_doctor=True)
        self.doctor = Doctor.objects.create(user=self.doctor_user, hospital=self.hospital, specialty="General")
        
        # Setup Emergency Case
        self.case = EmergencyCase.objects.create(
            hospital=self.hospital,
            patient_name="John Doe",
            symptoms="Severe Pain",
            severity="High",
            assigned_to=self.doctor_user,
            status="Open"
        )
        
        self.client = Client()

    def test_resolve_emergency_case(self):
        self.client.login(username='doctor', password='password')
        
        response = self.client.post(f'/emergency/resolve/{self.case.id}/', follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'Resolved')

    def test_check_staff_notifications_water(self):
        self.client.login(username='doctor', password='password')
        
        # Create Health Status with low water? 
        # API returns notifications based on logic. 
        # Currently logic is: if shift > 4h -> rest reminder.
        
        # Simulate Shift
        start_time = timezone.now() - timedelta(hours=4, minutes=1)
        StaffHealthStatus.objects.create(
            worker=self.doctor_user,
            date=timezone.now().date(),
            is_on_duty=True,
            shift_start=start_time,
            water_intake=0
        )
        
        response = self.client.get('/staff/notifications/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have rest reminder
        self.assertTrue(any(n['id'] == 'rest_reminder' for n in data['notifications']))
        
    def test_update_water_progress(self):
        self.client.login(username='doctor', password='password')
        
        # Initial state
        status, _ = StaffHealthStatus.objects.get_or_create(worker=self.doctor_user, date=timezone.now().date())
        self.assertEqual(status.water_intake, 0)
        
        # Add Water
        response = self.client.post(
            '/patient/update-health/', # Reusing existing endpoint
            data=json.dumps({'action': 'add_water'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['water'], 1)
        
        status.refresh_from_db()
        self.assertEqual(status.water_intake, 1)
