
from core.models import Doctor

# Find doctors with empty names
doctors = Doctor.objects.all()
for doc in doctors:
    if not doc.user.get_full_name().strip():
        print(f"Deleting ghost doctor: ID {doc.id}, User: {doc.user.username}")
        doc.user.delete() # Cascade deletes doctor profile
print("Cleanup complete.")
