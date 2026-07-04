from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import Hospital, Doctor, Staff, EmergencyCase, StaffHealthStatus
from django.utils import timezone
import datetime

class EmergencyRefinementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital_admin = User.objects.create_user(username='hosp_admin', password='password')
        self.hospital_admin.is_hospital_admin = True
        self.hospital_admin.save()
        self.hospital = Hospital.objects.create(user=self.hospital_admin, name="Test Hospital", address="123 Test St")
        
        # Create Doctor
        self.doctor_user = User.objects.create_user(username='doctor', password='password', first_name='Doc', last_name='Tor')
        self.doctor = Doctor.objects.create(user=self.doctor_user, hospital=self.hospital, specialty='Cardiology')
        self.doctor_user.is_doctor = True
        self.doctor_user.save()
        
        # Create Nurse
        self.nurse_user = User.objects.create_user(username='nurse', password='password', first_name='Nur', last_name='Se')
        self.nurse = Staff.objects.create(user=self.nurse_user, hospital=self.hospital, role='Nurse')
        self.nurse_user.is_nurse = True
        self.nurse_user.save()
        
        # Create Lab Tech
        self.lab_user = User.objects.create_user(username='lab', password='password')
        self.lab_user.is_lab = True
        self.lab_user.save()
        # Mock lab profile if needed (View checks User.objects.filter(lab_profile...))
        # Assuming simple User check in view for now or need profile
        
        # Login Doctor for creating case
        self.client.login(username='doctor', password='password')

    def test_create_emergency_case_identifies_support(self):
        # Set Nurse on duty
        StaffHealthStatus.objects.create(
            worker=self.nurse_user,
            hospital=self.hospital,
            date=timezone.now().date(),
            is_on_duty=True,
            shift_start=timezone.now() - datetime.timedelta(hours=2),
            water_intake=5
        )
        
        response = self.client.post(reverse('create_emergency_case'), {
            'patient_name': 'John Doe',
            'symptoms': 'Chest pain, needs blood test',
            'severity': 'Critical',
            'assigned_to': '' # Auto-assign
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0)
        msg_text = str(messages[0])
        
        # Check if Doctor assigned
        self.assertIn("Assigned to Doc Tor", msg_text)
        # Check if Support Team (Nurse) mentioned
        self.assertIn("Support Team Notified", msg_text)
        self.assertIn("Nurses", msg_text)

    def test_check_staff_notifications_returns_emergency(self):
        # Create an active emergency
        case = EmergencyCase.objects.create(
            hospital=self.hospital,
            patient_name='Jane Doe',
            symptoms='Broken leg',
            severity='Moderate',
            status='Open'
        )
        
        # Check as Nurse
        self.client.login(username='nurse', password='password')
        # Ensure Nurse has health status to pass the check
        StaffHealthStatus.objects.create(
            worker=self.nurse_user,
            hospital=self.hospital,
            date=timezone.now().date(),
            shift_start=timezone.now(),
            is_on_duty=True
        )
        
        response = self.client.get(reverse('check_staff_notifications'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have emergency notification
        found = False
        for n in data['notifications']:
             if f'emergency_{case.id}' == n['id']:
                 found = True
                 break
        self.assertTrue(found, "Emergency notification not found for Nurse")

    def test_check_staff_notifications_health_reminders(self):
        self.client.login(username='nurse', password='password')
        
        # Create Status with > 4 hours duration and low water
        start_time = timezone.now() - datetime.timedelta(hours=5)
        StaffHealthStatus.objects.create(
            worker=self.nurse_user,
            hospital=self.hospital,
            date=timezone.now().date(),
            start_time=start_time, # View might use start_time or shift_start -> View uses shift_start
            shift_start=start_time, 
            is_on_duty=True,
            water_intake=2
        )
        
        response = self.client.get(reverse('check_staff_notifications'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have rest reminder (> 4 hours)
        # Should have water reminder (intake < 4 and duration > 3)
        ids = [n['id'] for n in data['notifications']]
        self.assertIn('rest_reminder', ids)
        self.assertIn('water_reminder', ids)
