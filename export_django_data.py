import sqlite3
import json

def export_django_to_flutter_json(db_path='db.sqlite3', output='flutter_export.json'):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    flutter_data = {
        'users': [],
        'hospitals': [],
        'doctors': [],
        'patients': [],
        'appointments': [],
        'prescriptions': [],
        'medicines': [],
        'wards': [],
        'admissions': [],
        'emergencies': [],
        'notifications': [],
    }
    
    # Users
    cursor.execute("SELECT * FROM core_user")
    for row in cursor.fetchall():
        flutter_data['users'].append({
            'id': row['id'],
            'username': row['username'],
            'email': row['email'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'is_hospital_admin': bool(row['is_hospital_admin']),
            'is_doctor': bool(row['is_doctor']),
            'is_patient': bool(row['is_patient']),
            'is_lab': bool(row['is_lab']),
            'is_pharmacy': bool(row['is_pharmacy']),
            'is_staff_member': bool(row['is_staff_member']),
        })
    
    # Hospitals
    cursor.execute("SELECT * FROM core_hospital")
    for row in cursor.fetchall():
        flutter_data['hospitals'].append({
            'id': row['id'],
            'user_id': row['user_id'],
            'name': row['name'],
            'address': row['address'],
            'max_leave_days': row['max_leave_days'],
            'extra_leave_deduction': row['extra_leave_deduction'],
        })
    
    # Doctors
    cursor.execute("SELECT * FROM core_doctor")
    for row in cursor.fetchall():
        flutter_data['doctors'].append({
            'id': row['id'],
            'user_id': row['user_id'],
            'hospital_id': row['hospital_id'],
            'specialty': row['specialty'],
            'department': row['department'],
            'experience': row['experience'],
            'available': bool(row['available']),
        })
    
    # Patients
    cursor.execute("SELECT * FROM core_patient")
    for row in cursor.fetchall():
        flutter_data['patients'].append({
            'id': row['id'],
            'user_id': row['user_id'],
            'hospital_id': row['hospital_id'],
            'phone': row['phone'],
            'date_of_birth': row['date_of_birth'],
            'gender': row['gender'],
            'address': row['address'],
        })
    
    # Appointments
    cursor.execute("SELECT * FROM core_appointment")
    for row in cursor.fetchall():
        flutter_data['appointments'].append({
            'id': row['id'],
            'doctor_id': row['doctor_id'],
            'patient_id': row['patient_id'],
            'date': row['date'],
            'time': row['time'],
            'symptoms': row['symptoms'],
            'status': row['status'],
        })
    
    # Prescriptions
    cursor.execute("SELECT * FROM core_prescription")
    for row in cursor.fetchall():
        flutter_data['prescriptions'].append({
            'id': row['id'],
            'appointment_id': row['appointment_id'],
            'medicines': row['medicines'],
            'notes': row['notes'],
        })
    
    # Medicines
    cursor.execute("SELECT * FROM core_medicine")
    for row in cursor.fetchall():
        flutter_data['medicines'].append({
            'id': row['id'],
            'name': row['name'],
            'generic_name': row['generic_name'],
            'medicine_type': row['medicine_type'],
            'stock_quantity': row['stock_quantity'],
        })
    
    # Wards
    cursor.execute("SELECT * FROM core_ward")
    for row in cursor.fetchall():
        flutter_data['wards'].append({
            'id': row['id'],
            'hospital_id': row['hospital_id'],
            'ward_number': row['ward_number'],
            'ward_type': row['ward_type'],
        })
    
    # Patient Admissions
    cursor.execute("SELECT * FROM core_patientadmission")
    for row in cursor.fetchall():
        flutter_data['admissions'].append({
            'id': row['id'],
            'patient_id': row['patient_id'],
            'hospital_id': row['hospital_id'],
            'ward_id': row['ward_id'],
            'status': row['status'],
        })
    
    # Emergency Cases
    cursor.execute("SELECT * FROM core_emergencycase")
    for row in cursor.fetchall():
        flutter_data['emergencies'].append({
            'id': row['id'],
            'hospital_id': row['hospital_id'],
            'patient_name': row['patient_name'],
            'severity': row['severity'],
            'status': row['status'],
        })
    
    # Notifications
    cursor.execute("SELECT * FROM core_notification")
    for row in cursor.fetchall():
        flutter_data['notifications'].append({
            'id': row['id'],
            'recipient_id': row['recipient_id'],
            'message': row['message'],
            'type': row['type'],
        })
    
    conn.close()
    
    with open(output, 'w') as f:
        json.dump(flutter_data, f, indent=2)
    
    return flutter_data

if __name__ == '__main__':
    result = export_django_to_flutter_json()
    print(f"Exported {len(result['users'])} users")
    print(f"Exported {len(result['hospitals'])} hospitals")
    print(f"Exported {len(result['doctors'])} doctors")
    print(f"Exported {len(result['patients'])} patients")
    print(f"Exported {len(result['appointments'])} appointments")