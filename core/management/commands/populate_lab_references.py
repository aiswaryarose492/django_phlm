from django.core.management.base import BaseCommand
from core.models import LabTestReference

class Command(BaseCommand):
    help = 'Populates the database with default lab test reference ranges'

    def handle(self, *args, **kwargs):
        references = [
            # Hemoglobin
            {
                'test_name': 'Hemoglobin',
                'sex': 'Male',
                'min_age': 18,
                'max_age': 120,
                'condition': 'Any',
                'normal_range': '13.8 - 17.2',
                'unit': 'g/dL'
            },
            {
                'test_name': 'Hemoglobin',
                'sex': 'Female',
                'min_age': 18,
                'max_age': 120,
                'condition': 'Any',
                'normal_range': '12.1 - 15.1',
                'unit': 'g/dL'
            },
            {
                'test_name': 'Hemoglobin',
                'sex': 'Any',
                'min_age': 0,
                'max_age': 17,
                'condition': 'Any',
                'normal_range': '11.0 - 16.0',
                'unit': 'g/dL'
            },
            # Fasting Blood Sugar
            {
                'test_name': 'Fasting Blood Sugar',
                'sex': 'Any',
                'min_age': 0,
                'max_age': 120,
                'condition': 'Fasting',
                'normal_range': '70 - 99',
                'unit': 'mg/dL'
            }
        ]

        for ref in references:
            LabTestReference.objects.update_or_create(
                test_name=ref['test_name'],
                sex=ref['sex'],
                min_age=ref['min_age'],
                max_age=ref['max_age'],
                condition=ref['condition'],
                defaults={'normal_range': ref['normal_range'], 'unit': ref['unit']}
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated lab reference ranges'))
