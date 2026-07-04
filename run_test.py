
import subprocess
import sys

with open('out.txt', 'w', encoding='utf-8') as f:
    subprocess.run([sys.executable, 'manage.py', 'test', 'core.tests_emergency_flow.EmergencyFlowTest.test_staff_wellbeing_flow'], stdout=f, stderr=subprocess.STDOUT)
