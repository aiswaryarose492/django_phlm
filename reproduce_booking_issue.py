import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from core.models import Doctor, User, Hospital

def test_booking_flow():
    client = Client()
    
    print("--- Starting Booking Flow Test ---")

    # 1. Get a doctor
    doctor = Doctor.objects.first()
    if not doctor:
        print("ERROR: No doctors found in database.")
        return
    print(f"Target Doctor: {doctor} (ID: {doctor.id})")

    # 2. Test Doctor Selection Page
    print("\n[Step 1] Accessing Select Doctor Page...")
    response = client.get(reverse('select_doctor'))
    if response.status_code != 200:
        print(f"FAIL: Select Doctor page returned {response.status_code}")
        return
    print("PASS: Select Doctor page accessible.")

    # 3. Test Patient Details Form Submission
    print(f"\n[Step 2] Submitting Patient Details for Doctor {doctor.id}...")
    url = reverse('book_patient_details', kwargs={'doctor_id': doctor.id})
    patient_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        'phone': '9876543210',
        'age': '30',
        'gender': 'Male'
    }
    response = client.post(url, patient_data, follow=True)
    
    # Check if redirected to select_slot
    expected_url = reverse('select_slot', kwargs={'doctor_id': doctor.id})
    if expected_url not in response.request['PATH_INFO']:
         print(f"FAIL: Did not redirect to select_slot. Current URL: {response.request['PATH_INFO']}")
         # print(response.content.decode()) # Debug if needed
         return
    print("PASS: Redirected to Select Slot.")
    
    # Verify session data
    session = client.session
    if 'patient_details' not in session:
        print("FAIL: patient_details not found in session!")
        return
    print(f"PASS: Session data stored: {session['patient_details']}")

    # 4. Test Select Slot
    print("\n[Step 3] Accessing Select Slot Page...")
    # We need to pick a valid date/time. The view generates them.
    # Let's just try to access the page first.
    response = client.get(expected_url)
    if response.status_code != 200:
        print(f"FAIL: Select Slot page returned {response.status_code}")
        return
    print("PASS: Select Slot page accessible.")
    
    # Mocking a selection (assuming the view logic holds up, validation is in confirm step)
    # We need a valid future date
    from datetime import date, timedelta
    next_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    time_slot = "10:00 AM"

    # 5. Test Confirmation Page (GET)
    print("\n[Step 4] Accessing Confirmation Page...")
    confirm_url = reverse('confirm_appointment')
    # pass params via GET as the JS does
    response = client.get(f"{confirm_url}?doctor_id={doctor.id}&date={next_date}&time={time_slot}")
    
    if response.status_code != 200:
        print(f"FAIL: Confirmation page returned {response.status_code}")
        # print(response.content.decode())
        return
    print("PASS: Confirmation page accessible.")

    # 6. Test Booking Submission (POST)
    print("\n[Step 5] Submitting Final Booking...")
    # The view expects doctor_id, date, time in POST or GET.
    # It also handles user creation if not authenticated.
    
    post_data = {
        'doctor_id': doctor.id,
        'appointment_date': next_date,
        'appointment_time': time_slot,
        'consultation_type': 'offline',
        'symptoms': 'Test symptoms',
        'csrfmiddlewaretoken': client.cookies['csrftoken'].value if 'csrftoken' in client.cookies else ''
    }
    
    # We need to ensure we are LOGGED OUT to test the auto-login/creation flow
    client.logout()
    
    # Manually set session for functionality (since we logged out)
    session = client.session
    session['patient_details'] = patient_data
    session.save()

    try:
        response = client.post(confirm_url, post_data)
    except Exception as e:
        print(f"FAIL: Crashed during POST: {e}")
        return

    if response.status_code != 200:
        print(f"FAIL: Booking submission returned {response.status_code}")
        # print(response.content.decode()) 
        return
        
    # Check for success template or content
    if 'Booking Confirmed' in response.content.decode() or 'booking_success.html' in [t.name for t in response.templates]:
        print("PASS: Booking Successful!")
        # Check if user is logged in
        if '_auth_user_id' in client.session:
             print("PASS: Auto-login successful.")
        else:
             print("FAIL: Auto-login failed (User not in session).")
    else:
        print("FAIL: Success page not rendered.")
        # print(response.content.decode())

    # 7. Test Legacy Redirect
    print("\n[Step 6] Testing Legacy URL Redirect...")
    legacy_url = reverse('book_appointment')
    response = client.get(legacy_url, follow=True)
    
    if response.redirect_chain:
        # Check if it eventually lands on select_doctor or login
        final_url = response.redirect_chain[-1][0]
        print(f"Legacy URL redirected to: {final_url}")
        if 'login' in final_url or 'select-doctor' in final_url:
             print("PASS: Legacy URL handles redirect correctly.")
        else:
             print(f"WARN: Legacy URL redirected to unexpected: {final_url}")
    else:
        print(f"FAIL: Legacy URL did not redirect. Status: {response.status_code}")

if __name__ == "__main__":
    test_booking_flow()
