from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import User, Patient, Reminder, Hospital

class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital_user = User.objects.create_user(username='hospital_admin', password='password123', is_hospital_admin=True)
        self.hospital = Hospital.objects.create(user=self.hospital_user, name="Test Hospital", address="Test Address")
        self.user = User.objects.create_user(username='patient1', password='password123', is_patient=True)
        self.patient = Patient.objects.create(user=self.user, hospital=self.hospital)
        self.client.force_login(self.user)

    def test_get_due_reminders(self):
        # Create a reminder due now
        now = timezone.now()
        r1 = Reminder.objects.create(
            patient=self.patient,
            type='Medicine',
            message='Take Pill A',
            time=now.time(),
            is_active=True
        )
        
        # Create a reminder in the future
        future_time = (now + timedelta(hours=2)).time()
        r2 = Reminder.objects.create(
            patient=self.patient,
            type='Medicine',
            message='Take Pill B',
            time=future_time,
            is_active=True
        )
        
        url = reverse('get_due_reminders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data['reminders']), 1)
        self.assertEqual(data['reminders'][0]['id'], r1.id)
        self.assertEqual(data['reminders'][0]['message'], 'Take Pill A')
