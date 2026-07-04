
from core.models import Doctor

doctors = Doctor.objects.all()
print(f"Total doctors: {doctors.count()}")
print("--- START REPORT ---")
for doc in doctors:
    full_name = doc.user.get_full_name()
    print(f"ID: {doc.id}, Name: '{full_name}', Specialty: '{doc.specialty}', Available: {doc.available}")
print("--- END REPORT ---")
