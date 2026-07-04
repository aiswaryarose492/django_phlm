import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

from core.models import User

try:
    user = User.objects.get(username='azeezia')
    if not user.is_hospital_admin:
        user.is_hospital_admin = True
        user.save()
        print("SUCCESS: User 'azeezia' is now a Hospital Admin.")
    else:
        print("INFO: User 'azeezia' was already a Hospital Admin.")
except User.DoesNotExist:
    print("ERROR: User 'azeezia' does not exist. Please create it first via the Admin panel.")
