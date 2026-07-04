from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Patient, Hospital

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate 10 unique patients with default credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hospital-id',
            type=int,
            help='Hospital ID to associate patients with',
        )

    def handle(self, *args, **options):
        hospital_id = options.get('hospital_id')

        if hospital_id:
            try:
                hospital = Hospital.objects.get(id=hospital_id)
            except Hospital.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Hospital with ID {hospital_id} not found'))
                return
        else:
            hospital = Hospital.objects.first()
            if not hospital:
                self.stdout.write(self.style.ERROR('No hospitals found. Please create a hospital first.'))
                return

        self.stdout.write(f'Creating patients for hospital: {hospital.name}')

        patients_data = [
            ('Manu', 'Male', 'manu'),
            ('Sweetha', 'Female', 'sweetha'),
            ('Seethal', 'Female', 'seethal'),
            ('Lilly', 'Female', 'lilly'),
            ('Ambhika', 'Female', 'ambhika'),
            ('Manoj', 'Male', 'manoj'),
            ('Arun', 'Male', 'arun'),
            ('Divya', 'Female', 'divya'),
            ('Rahul', 'Male', 'rahul'),
            ('Priya', 'Female', 'priya'),
        ]

        password = '1234'
        count = 0

        for name, gender, username in patients_data:
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': name,
                    'last_name': '',
                    'is_patient': True,
                    'is_active': True,
                }
            )

            if user_created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'  Created user: {username}')
            else:
                user.first_name = name
                user.last_name = ''
                user.is_patient = True
                user.set_password(password)
                user.save()
                self.stdout.write(f'  Updated user: {username}')

            patient, patient_created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'hospital': hospital,
                    'gender': gender,
                }
            )

            if patient_created:
                count += 1
                self.stdout.write(f'  Created patient: {name}')
            else:
                patient.hospital = hospital
                patient.gender = gender
                patient.save()
                self.stdout.write(f'  Updated patient: {name}')

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {count} patients'))
        self.stdout.write(self.style.SUCCESS(f'Total patients in database: {Patient.objects.count()}'))
