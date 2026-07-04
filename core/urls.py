from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hospital/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hospital/doctors/', views.hospital_doctors, name='hospital_doctors'),
    path('hospital/staff/', views.hospital_staff, name='hospital_staff'),
    path('hospital/patients/', views.hospital_patients, name='hospital_patients'),
    path('hospital/emergency/', views.hospital_emergency, name='hospital_emergency'),
    path('hospital/attendance/', views.hospital_attendance, name='hospital_attendance'),
    path('hospital/attendance/history/<int:user_id>/', views.staff_attendance_history, name='staff_attendance_history'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    # path('hospital/add-patient/', views.add_patient, name='add_patient'),
    path('hospital/remove-staff/<int:user_id>/', views.remove_staff, name='remove_staff'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path('doctor/reports/', views.doctor_reports, name='doctor_reports'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/start-meet/<int:appointment_id>/', views.start_meet, name='start_meet'),
    path('doctor/update-meet-link/<int:appointment_id>/', views.update_meet_link, name='update_meet_link'),
    path('doctor/notify-next-patient/<int:appointment_id>/', views.notify_next_patient, name='notify_next_patient'),
    path('doctor/toggle-shift/', views.toggle_shift, name='toggle_shift'),
    path('doctor/update-availability/', views.update_doctor_availability, name='update_doctor_availability'),
    path('doctor/apply-leave/', views.apply_leave, name='apply_leave'),
    path('hospital/manage-leave/', views.manage_leave_requests, name='manage_leave_requests'),
    path('hospital/schedule/', views.schedule_staff, name='schedule_staff'),
    path('doctor/prescription/<int:appointment_id>/', views.add_prescription, name='add_prescription'),
    path('doctor/appointments-for-prescription/', views.get_appointments_for_prescription, name='get_appointments_for_prescription'),
    path('doctor/past-prescription/<int:patient_id>/', views.get_past_prescription, name='get_past_prescription'),
    path('doctor/appointments-for-test/', views.get_appointments_for_test, name='get_appointments_for_test'),
    path('doctor/test-request/<int:appointment_id>/', views.request_test, name='request_test'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/book/', views.book_appointment, name='book_appointment'),
    path('patient/book/select-doctor/', views.select_doctor, name='select_doctor'),
    path('patient/book/details/<int:doctor_id>/', views.book_patient_details, name='book_patient_details'),
    path('patient/book/select-slot/<int:doctor_id>/', views.select_slot, name='select_slot'),
    path('patient/book/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('patient/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('patient/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('patient/update-health/', views.update_health_status, name='update_health_status'),
    path('patient/complete-reminder/<int:reminder_id>/', views.complete_reminder, name='complete_reminder'),
    path('patient/create-reminder/', views.create_reminder, name='create_reminder'),
    path('patient/delete-reminder/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
    path('patient/get-due-reminders/', views.get_due_reminders, name='get_due_reminders'),

    # OTP Verification
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # Lab
    path('lab_dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('lab/upload_report/<int:request_id>/', views.upload_report, name='upload_report'),
    path('lab/upload_test/', views.upload_lab_test, name='upload_lab_test'),
    path('lab/process/<int:report_id>/', views.lab_process_report, name='lab_process_report'),
    
    # Pharmacy
    path('pharmacy/', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('pharmacy/process/<int:prescription_id>/', views.process_prescription, name='process_prescription'),
    path('pharmacy/toggle-shift/', views.toggle_pharmacy_shift, name='toggle_pharmacy_shift'),
    path('pharmacy/update-water/', views.update_pharmacy_water, name='update_pharmacy_water'),
    path('pharmacy/dispense-medicine/<int:prescribed_medicine_id>/', views.dispense_medicine, name='dispense_medicine'),
    path('pharmacy/mark-external/<int:prescribed_medicine_id>/', views.mark_medicine_external, name='mark_medicine_external'),
    path('mark-dispensed/<int:prescription_id>/', views.mark_as_dispensed, name='mark_as_dispensed'),
    
    # Generic Staff & Emergency

    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/toggle-shift/', views.toggle_staff_shift, name='toggle_staff_shift'),
    path('staff/update-water/', views.update_staff_water, name='update_staff_water'),
    path('emergency/create/', views.create_emergency_case, name='create_emergency_case'),
    path('emergency/notifications/', views.get_emergency_notifications, name='get_emergency_notifications'),
    path('emergency/resolve/<int:case_id>/', views.resolve_emergency_case, name='resolve_emergency_case'),
    path('emergency/delete/<int:case_id>/', views.delete_emergency_case, name='delete_emergency_case'),
    path('staff/notifications/', views.check_staff_notifications, name='check_staff_notifications'),
    path('notifications/read/<str:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # ==================== EXTENDED MODULES ====================
    
    # Emergency Module Extensions
    path('emergency/enhanced/create/', views.create_enhanced_emergency, name='create_enhanced_emergency'),
    path('emergency/alarms/', views.get_active_alarms, name='get_active_alarms'),
    path('emergency/alarm/acknowledge/<int:alarm_id>/', views.acknowledge_alarm, name='acknowledge_alarm'),
    
    # Ward Management
    path('hospital/wards/', views.manage_wards, name='manage_wards'),
    
    # Patient Admission
    path('admission/create/', views.admit_patient, name='admit_patient'),
    path('admission/<int:admission_id>/discharge/', views.discharge_patient, name='discharge_patient'),
    path('admission/<int:admission_id>/details/', views.view_admission_details, name='view_admission_details'),
    
    # Nurse Monitoring Panel
    path('nurse/monitoring/', views.nurse_monitoring_panel, name='nurse_monitoring_panel'),
    path('nurse/monitoring/log/<int:admission_id>/', views.add_monitoring_log, name='add_monitoring_log'),
    path('nurse/water-intake/<int:admission_id>/', views.log_water_intake, name='log_water_intake'),
    path('nurse/my-water-intake/', views.log_nurse_water_intake, name='log_nurse_water_intake'),
    path('nurse/mark-task/<int:admission_id>/', views.mark_task_complete, name='mark_task_complete'),
    path('nurse/ward-updates/', views.get_ward_updates, name='get_ward_updates'),
    path('nurse/injection/schedule/<int:admission_id>/', views.schedule_injection, name='schedule_injection'),
    
    # Pharmacy Extensions
    path('pharmacy/medicines/', views.manage_medicines, name='manage_medicines'),
    path('pharmacy/medicines/json/', views.get_medicines_json, name='get_medicines_json'),
    path('doctor/prescription/enhanced/<int:appointment_id>/', views.prescribe_medicine_with_db, name='prescribe_medicine_with_db'),
    
    # Ambulance Module
    path('ambulance/dashboard/', views.ambulance_dashboard, name='ambulance_dashboard'),
    path('ambulance/manage/', views.manage_ambulance, name='manage_ambulance'),
    path('ambulance/request/', views.request_ambulance, name='request_ambulance'),
    path('ambulance/call/<int:call_id>/update/', views.update_ambulance_status, name='update_ambulance_status'),
    path('ambulance/emergency-alert/', views.ambulance_emergency_alert, name='ambulance_emergency_alert'),
    
    # Patient Billing & Payment
    path('patient/billing/', views.patient_billing, name='patient_billing'),
    path('patient/payment/<int:admission_id>/', views.process_payment, name='process_payment'),
]
