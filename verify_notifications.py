
import os
import django
import sys
import json


# Setup Django environment
sys.path.append('d:\\phlm_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

# Configure ALLOWED_HOSTS for test client
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

from core.models import User, Hospital, Doctor, Staff, EmergencyCase, Notification, WorkLog, StaffHealthStatus
from django.test import Client, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from core.views import create_emergency_case, check_staff_notifications
from django.utils import timezone

def verify_notifications():
    print("Starting Verification...")
    
    try:
        # 1. Setup Data
        username = 'debug_admin_notif'
        if not User.objects.filter(username=username).exists():
            admin_user = User.objects.create_user(username=username, password='password', is_hospital_admin=True)
            hospital = Hospital.objects.create(user=admin_user, name="Notif Test Hospital", address="123 Notif St")
        else:
            admin_user = User.objects.get(username=username)
            hospital = admin_user.hospital_profile

        # Create Doctor
        doc_username = 'dr_notif'
        if not User.objects.filter(username=doc_username).exists():
        # 3. Create Doctor
            doc_user = User.objects.create_user(username='dr_notif', password='password', is_doctor=True)
            date = timezone.now().date()
            doc = Doctor.objects.create(user=doc_user, hospital=hospital, specialty='Cardiology', available=True)
            # Create worklog for doctor to be "on duty"
            WorkLog.objects.create(doctor=doc, date=date, start_time=timezone.now())
        else:
            doc_user = User.objects.get(username=doc_username)
            doc = doc_user.doctor_profile

        # Create Nurse
        nurse_username = 'nurse_notif'
        if not User.objects.filter(username=nurse_username).exists():
        # 4. Create Nurse
            nurse_user = User.objects.create_user(username='nurse_notif', password='password', is_staff_member=True)
            nurse = Staff.objects.create(user=nurse_user, hospital=hospital, role='Nurse')
            # Create health status for nurse to be "on duty"
            StaffHealthStatus.objects.create(worker=nurse_user, date=date, is_on_duty=True)
        else:
            nurse_user = User.objects.get(username=nurse_username)

        # 2. Test Emergency Case Creation & Notification Generation
        print("Testing Emergency Case Creation...")
        client = Client()
        client.force_login(admin_user)
        
        data = {
            'patient_name': 'Emergency Patient X',
            'symptoms': 'Chest Pain, Difficulty Breathing',
            'severity': 'Critical',
            'assigned_to': '' # Auto-assign
        }
        
        # response = client.post('/emergency/create/', data, follow=True) # Duplicate call removed
        
        response = client.post('/emergency/create/', data, follow=True)
        
        print(f"View Response Code: {response.status_code}")
        if hasattr(response, 'redirect_chain'):
            print(f"Redirect Chain: {response.redirect_chain}")
        
        # Check messages
        messages = list(response.context['messages']) if response.context else []
        for m in messages:
            print(f"Message: {m}")
        
        # Check if case created
        case = EmergencyCase.objects.filter(patient_name='Emergency Patient X').order_by('-created_at').first()
        if case:
            print(f"SUCCESS: Emergency Case created. ID: {case.id}")
        else:
            print("FAILURE: Emergency Case not created.")
            
        # Check Notifications for Doctor
        doc_notif = Notification.objects.filter(recipient=doc_user, type='Emergency').order_by('-created_at').first()
        if doc_notif:
             print(f"SUCCESS: Notification created for Doctor: {doc_notif.message}")
        else:
             print("FAILURE: No notification for Doctor.")

        # Check Notifications for Nurse
        nurse_notif = Notification.objects.filter(recipient=nurse_user, type='Emergency').order_by('-created_at').first()
        if nurse_notif:
             print(f"SUCCESS: Notification created for Nurse: {nurse_notif.message}")
        else:
             print("FAILURE: No notification for Nurse.")

        # 3. Test check_staff_notifications View
        print("\nTesting check_staff_notifications API...")
        
        # Use Factory for GET request as it is simpler for APIs or use Client
        factory = RequestFactory()
        req_notif = factory.get('/staff/notifications/')
        req_notif.user = doc_user
        
        response = check_staff_notifications(req_notif)
        content = json.loads(response.content.decode('utf-8'))
        
        if 'notifications' in content:
            found = False
            for n in content['notifications']:
                if 'Emergency Patient X' in n['message']:
                    print(f"SUCCESS: API returned correct notification: {n['title']} - {n['message']}")
                    found = True
                    break
            if not found:
                 print("FAILURE: API did not return the new notification.")
                 print(f"Returned: {content['notifications']}")
        else:
            print("FAILURE: API response malformed.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nCleaning up...")
        User.objects.filter(username__in=['debug_admin_notif', 'dr_notif', 'nurse_notif']).delete()
        if 'case' in locals() and case:
            case.delete()

if __name__ == '__main__':
    verify_notifications()
