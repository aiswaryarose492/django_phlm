import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phlms_project.settings')
django.setup()

from core.templatetags.medicine_tags import parse_medicines

medicines_json = json.dumps([
    {"name": "Paracetamol 500mg", "timing": "1-0-1", "condition": "After Food", "is_available": True},
    {"name": "Rare Medicine 100mg", "timing": "0-0-1", "condition": "Before Sleep", "is_available": False}
])

html_output = parse_medicines(medicines_json)
print("--- OUTPUT ---")
print(html_output)
print("--------------")

assert "Not available in Pharmacy" in html_output
assert "Rare Medicine 100mg" in html_output
assert "Paracetamol" in html_output
print("Test passed successfully!")
