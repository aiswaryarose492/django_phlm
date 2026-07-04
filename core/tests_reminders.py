from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Patient, Reminder, Hospital

class ReminderCompletionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hospital_user = User.objects.create_user(username='hospital_admin', password='password123', is_hospital_admin=True)
        self.hospital = Hospital.objects.create(user=self.hospital_user, name="Test Hospital", address="Test Address")
        self.user = User.objects.create_user(username='patient1', password='password123', is_patient=True)
        self.patient = Patient.objects.create(user=self.user, hospital=self.hospital)
        self.reminder = Reminder.objects.create(
            patient=self.patient,
            type='Medicine',
            message='Take pill',
            time='08:00',
            is_active=True
        )
        self.client.login(username='patient1', password='password123')

    def test_complete_reminder(self):
        # Verify initial state
        self.assertIsNone(self.reminder.last_taken)

        # Call the completion view
        response = self.client.post(reverse('complete_reminder', args=[self.reminder.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Verify database update
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.last_taken, timezone.now().date())

    def test_dashboard_context(self):
        # Initial check
        response = self.client.get(reverse('patient_dashboard'))
        self.assertFalse(response.context['reminders'][0].is_completed_today)

        # Complete reminder
        self.client.post(reverse('complete_reminder', args=[self.reminder.id]))

        # Check context again
        response = self.client.get(reverse('patient_dashboard'))
        self.assertTrue(response.context['reminders'][0].is_completed_today)
