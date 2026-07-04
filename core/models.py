from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    is_hospital_admin = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_lab = models.BooleanField(default=False)
    is_pharmacy = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)

class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=255)
    address = models.TextField()
    max_leave_days = models.IntegerField(default=12, help_text="Maximum allowed leave days per year")
    extra_leave_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Salary deduction per extra leave day")
    latitude = models.FloatField(null=True, blank=True, help_text="Hospital Latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="Hospital Longitude")
    allowed_ip_address = models.CharField(max_length=255, null=True, blank=True, help_text="Comma-separated IP addresses allowed for marking attendance (e.g. 192.168.1.1, 203.0.113.5)")

    def __str__(self):
        return self.name

class Doctor(models.Model):
    DEPARTMENT_CHOICES = [
        ('General Medicine', 'General Medicine'),
        ('Cardiology', 'Cardiology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Orthopedics', 'Orthopedics'),
        ('Dermatology', 'Dermatology'),
        ('Ophthalmology', 'Ophthalmology'),
        ('ENT', 'ENT'),
        ('Gynecology', 'Gynecology'),
        ('Psychiatry', 'Psychiatry'),
        ('Physiotherapy', 'Physiotherapy'),
        ('Dental', 'Dental'),
        ('Emergency', 'Emergency'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='General Medicine', help_text="Doctor's department")
    image = models.ImageField(upload_to='doctors/', blank=True, null=True, help_text="Doctor's photo")
    qualification = models.CharField(max_length=200, blank=True, default='')
    experience = models.IntegerField(default=0, help_text="Years of experience")
    bio = models.TextField(blank=True, default='', help_text="Brief biography")
    available = models.BooleanField(default=True, help_text="Availability for appointments")
    
    # Availability Schedule
    available_days = models.CharField(max_length=100, default='Monday,Tuesday,Wednesday,Thursday,Friday', 
        help_text="Days available (comma separated: Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday)")
    available_start_time = models.TimeField(null=True, blank=True, help_text="Start of working hours")
    available_end_time = models.TimeField(null=True, blank=True, help_text="End of working hours")
    break_start_time = models.TimeField(null=True, blank=True, help_text="Start of break/ward rounds")
    break_end_time = models.TimeField(null=True, blank=True, help_text="End of break/ward rounds")
    max_appointments_per_day = models.IntegerField(default=10, help_text="Maximum appointments per day")
    appointment_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Consultation fees")
    
    # Financials
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    salary_frequency = models.CharField(max_length=20, choices=[('Monthly', 'Monthly'), ('Weekly', 'Weekly')], default='Monthly')

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

    def get_total_approved_leave_days(self):
        # Calculate total days of approved leave in current year
        import datetime
        current_year = datetime.date.today().year
        leaves = self.leave_requests.filter(status='Approved', start_date__year=current_year)
        total_days = 0
        for leave in leaves:
            # Simple difference + 1 for inclusive
            days = (leave.end_date - leave.start_date).days + 1
            total_days += days
        return total_days
    
    def get_salary_deduction(self):
        total_leave = self.get_total_approved_leave_days()
        max_allowed = self.hospital.max_leave_days
        if total_leave > max_allowed:
            extra_days = total_leave - max_allowed
            deduction = extra_days * self.hospital.extra_leave_deduction
            return deduction
        return 0

    def get_final_salary(self):
        # Assuming salary is monthly, we might want to show "Current Month Salary" or "Base Salary"
        # For simplicity, if we are just showing "Deduction applicable", we can return base - deduction
        # But salary frequency matters. Let's just return the deduction amount for display mostly.
        return self.salary - self.get_salary_deduction()


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Emergency Leave', 'Emergency Leave'),
        ('Annual Leave', 'Annual Leave'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES, default='Casual Leave')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Leave request by Dr. {self.doctor.user.get_full_name()} from {self.start_date} to {self.end_date}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other')
    address = models.TextField(default='')
    water_goal = models.IntegerField(default=8, help_text="Daily water intake goal in glasses")

    @property
    def age(self):
        if not self.date_of_birth:
            return 0
        import datetime
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return self.user.get_full_name()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    symptoms = models.TextField()
    is_online = models.BooleanField(default=False)
    meet_link = models.URLField(max_length=500, null=True, blank=True, help_text="Video consultation link (auto-generated or manually set by doctor)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
        # Auto-generate Google Meet link for online appointments if missing
        if self.is_online and not self.meet_link:
            unique_id = uuid.uuid4().hex[:10]
            formatted_id = f"{unique_id[:3]}-{unique_id[3:7]}-{unique_id[7:10]}"
            self.meet_link = f"https://meet.google.com/{formatted_id}"
        super().save(*args, **kwargs)

class LabReport(models.Model):
    TEST_TYPE_CHOICES = [
        ('Blood Test', 'Blood Test'),
        ('Urine Test', 'Urine Test'),
        ('X-Ray', 'X-Ray'),
        ('MRI', 'MRI'),
        ('CT Scan', 'CT Scan'),
        ('ECG', 'ECG'),
        ('Ultrasound', 'Ultrasound'),
        ('Other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    test_type = models.CharField(max_length=50, choices=TEST_TYPE_CHOICES, default='Blood Test')
    file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    
    # Patient can upload their test image/document
    patient_upload = models.FileField(upload_to='patient_uploads/', blank=True, null=True)
    patient_uploaded_at = models.DateTimeField(blank=True, null=True)
    
    # Lab staff can add results
    result = models.TextField(blank=True, help_text="Lab technician's findings and analysis")
    result_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    result_uploaded_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey('LabWorker', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def clean_title(self):
        if self.title.startswith('Lab Request:'):
            return self.title.replace('Lab Request:', '', 1).strip()
        return self.title

class Staff(models.Model):
    STAFF_ROLES = [
        ('Nurse', 'Nurse'),
        ('Other', 'Other Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='Nurse')
    phone = models.CharField(max_length=15, default='')
    image = models.ImageField(upload_to='staff/', blank=True, null=True, help_text="Staff photo")
    # Duty scheduling fields
    duty_date = models.DateField(null=True, blank=True)
    duty_start = models.TimeField(null=True, blank=True)
    duty_end = models.TimeField(null=True, blank=True)
    notes = models.TextField(default='', blank=True)
    
    # Financials
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    salary_frequency = models.CharField(max_length=20, choices=[('Monthly', 'Monthly'), ('Weekly', 'Weekly')], default='Monthly')

    # Availability Schedule
    available_days = models.CharField(max_length=100, default='Monday,Tuesday,Wednesday,Thursday,Friday', 
        help_text="Days available (comma separated)")
    available_start_time = models.TimeField(null=True, blank=True, help_text="Start of working hours")
    available_end_time = models.TimeField(null=True, blank=True, help_text="End of working hours")

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

class LabWorker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lab_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='')
    image = models.ImageField(upload_to='lab_workers/', blank=True, null=True, help_text="Lab Worker photo")

    # Financials
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    salary_frequency = models.CharField(max_length=20, choices=[('Monthly', 'Monthly'), ('Weekly', 'Weekly')], default='Monthly')

    # Availability Schedule
    available_days = models.CharField(max_length=100, default='Monday,Tuesday,Wednesday,Thursday,Friday', 
        help_text="Days available (comma separated)")
    available_start_time = models.TimeField(null=True, blank=True, help_text="Start of working hours")
    available_end_time = models.TimeField(null=True, blank=True, help_text="End of working hours")

    def __str__(self):
        return self.user.get_full_name()

class PharmacyWorker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='')
    image = models.ImageField(upload_to='pharmacy_workers/', blank=True, null=True, help_text="Pharmacy Worker photo")

    # Financials
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    salary_frequency = models.CharField(max_length=20, choices=[('Monthly', 'Monthly'), ('Weekly', 'Weekly')], default='Monthly')

    # Availability Schedule
    available_days = models.CharField(max_length=100, default='Monday,Tuesday,Wednesday,Thursday,Friday', 
        help_text="Days available (comma separated)")
    available_start_time = models.TimeField(null=True, blank=True, help_text="Start of working hours")
    available_end_time = models.TimeField(null=True, blank=True, help_text="End of working hours")

    def __str__(self):
        return self.user.get_full_name()

class StaffHealthStatus(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    water_intake = models.IntegerField(default=0)
    is_on_duty = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False, help_text="Marked present for the day")
    shift_start = models.DateTimeField(null=True, blank=True)
    # Add other wellbeing fields if needed
    
    class Meta:
        unique_together = ('worker', 'date')

class Reminder(models.Model):
    REMINDER_TYPES = [
        ('Medicine', 'Medicine'),
        ('Water', 'Water'),
        ('Appointment', 'Appointment'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=REMINDER_TYPES)
    message = models.CharField(max_length=255)
    time = models.TimeField()
    last_taken = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class WorkLog(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    def duration(self):
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600 # hours
        return 0

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    medicines = models.TextField(help_text="Format: Medicine Name - Dosage - Frequency")
    notes = models.TextField(blank=True)
    is_dispensed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_parsed_medicines(self):
        import json
        text = self.medicines.strip()
        if text.startswith('[') and text.endswith(']'):
            try:
                return json.loads(text)
            except:
                pass
        return None
    
    def get_prescribed_medicines(self):
        """Get medicines from PrescribedMedicine table (new system)"""
        return self.prescribed_medicines.all().select_related('medicine')

class TestRequest(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='test_requests')
    test_name = models.CharField(max_length=200)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

class DailyHealthStatus(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    water_intake = models.IntegerField(default=0, help_text="Number of glasses")
    meditation_done = models.BooleanField(default=False)
    healthy_food = models.BooleanField(default=False)
    step_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('patient', 'date')
        
    @property
    def water_percentage(self):
        return min(self.water_intake * 12.5, 100)

    def health_score(self):
        score = 0
        if self.water_intake >= 8: score += 40
        elif self.water_intake >= 4: score += 20
        if self.meditation_done: score += 30
        if self.healthy_food: score += 30
        return min(score, 100)

class EmergencyCase(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    SEVERITY_CHOICES = [
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Critical', 'Critical'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=255)
    symptoms = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='emergency_cases')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.severity}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=50, default='General') # Emergency, General
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.type} Notification for {self.recipient.username}"

class LabTestReference(models.Model):
    """Stores the normal reference ranges for lab tests based on demographics"""
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Any', 'Any'),
    ]
    
    test_name = models.CharField(max_length=200, help_text="Exact name of the test, e.g., 'Hemoglobin'")
    sex = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Any', help_text="Gender this range applies to")
    min_age = models.IntegerField(default=0, help_text="Minimum age in years")
    max_age = models.IntegerField(default=120, help_text="Maximum age in years")
    condition = models.CharField(max_length=100, default='Any', help_text="Special conditions, e.g., 'Fasting'")
    normal_range = models.CharField(max_length=100, help_text="The normal range to display, e.g., '13.8 - 17.2'")
    unit = models.CharField(max_length=50, help_text="Unit of measurement, e.g., 'g/dL'")
    
    class Meta:
        ordering = ['test_name', 'sex', 'min_age']
        unique_together = ('test_name', 'sex', 'min_age', 'max_age', 'condition')

    def __str__(self):
        return f"{self.test_name} ({self.sex}, {self.min_age}-{self.max_age}y) -> {self.normal_range} {self.unit}"


# ==================== EXTENDED MODELS FOR ADVANCED MODULES ====================

class Ward(models.Model):
    """Ward/Room management for patient admissions"""
    WARD_TYPES = [
        ('General', 'General Ward'),
        ('Private', 'Private Room'),
        ('ICU', 'Intensive Care Unit'),
        ('Emergency', 'Emergency Ward'),
        ('Maternity', 'Maternity Ward'),
        ('Pediatric', 'Pediatric Ward'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='wards')
    ward_number = models.CharField(max_length=50)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPES, default='General')
    floor = models.CharField(max_length=20, default='1')
    total_beds = models.IntegerField(default=10)
    occupied_beds = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    nurses = models.ManyToManyField(Staff, blank=True, related_name='assigned_wards',
        limit_choices_to={'role': 'Nurse'}, help_text="Nurses assigned to this ward")
    
    class Meta:
        unique_together = ('hospital', 'ward_number')
    
    @property
    def available_beds(self):
        return self.total_beds - self.occupied_beds
    
    @property
    def occupancy_rate(self):
        if self.total_beds > 0:
            return (self.occupied_beds / self.total_beds) * 100
        return 0
    
    def __str__(self):
        return f"{self.ward_number} ({self.ward_type}) - {self.hospital.name}"


class PatientAdmission(models.Model):
    """Patient admission tracking"""
    STATUS_CHOICES = [
        ('Admitted', 'Admitted'),
        ('Under Treatment', 'Under Treatment'),
        ('Critical', 'Critical'),
        ('Stable', 'Stable'),
        ('Discharged', 'Discharged'),
        ('Transferred', 'Transferred'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='admissions')
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, related_name='admissions')
    bed_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Admission details
    admission_reason = models.TextField(help_text="Reason for admission")
    admitting_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='admitted_patients')
    admission_date = models.DateTimeField(auto_now_add=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Admitted')
    is_serious = models.BooleanField(default=False, help_text="Marked as serious case")
    
    # Treatment plan link
    treatment_plan = models.TextField(blank=True, help_text="Treatment plan notes")
    
    # Billing
    total_bill = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bill_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Assigned nurses (auto-assigned)
    assigned_nurses = models.ManyToManyField(Staff, blank=True, related_name='assigned_patients', limit_choices_to={'role': 'Nurse'})
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.ward} - {self.status}"
    
    @property
    def admission_days(self):
        from datetime import date
        if self.discharge_date:
            return (self.discharge_date.date() - self.admission_date.date()).days
        return (date.today() - self.admission_date.date()).days
    
    @property
    def outstanding_amount(self):
        return self.total_bill - self.bill_paid


class NurseWorkload(models.Model):
    """Track nurse workload for auto-assignment"""
    nurse = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='workload', limit_choices_to={'role': 'Nurse'})
    active_patients = models.IntegerField(default=0, help_text="Number of patients currently assigned")
    max_patients = models.IntegerField(default=5, help_text="Maximum patients nurse can handle")
    is_available = models.BooleanField(default=True)
    last_assigned = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nurse.user.get_full_name()} - {self.active_patients}/{self.max_patients} patients"
    
    @property
    def workload_percentage(self):
        if self.max_patients > 0:
            return (self.active_patients / self.max_patients) * 100
        return 0


class PatientWaterIntake(models.Model):
    """Track patient water intake per shift"""
    SHIFT_CHOICES = [
        ('Morning', 'Morning (6AM - 2PM)'),
        ('Afternoon', 'Afternoon (2PM - 10PM)'),
        ('Night', 'Night (10PM - 6AM)'),
    ]
    
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, related_name='water_intakes')
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    date = models.DateField(auto_now_add=True)
    glasses = models.IntegerField(default=0, help_text="Number of glasses consumed")
    recorded_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='recorded_water_intakes')
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('admission', 'shift', 'date')
    
    def __str__(self):
        return f"{self.admission.patient.user.get_full_name()} - {self.shift}: {self.glasses} glasses"


class NurseTaskLog(models.Model):
    """Track daily nursing tasks per shift - shared across all ward nurses"""
    TASK_CHOICES = [
        ('Medicine', 'Medicine Given'),
        ('Injection', 'Injection Given'),
        ('Infection', 'Infection Check'),
        ('Vitals', 'Vitals Recorded'),
        ('Water', 'Water Intake Recorded'),
        ('Diet', 'Diet Check'),
    ]
    
    SHIFT_CHOICES = [
        ('Morning', 'Morning (6AM - 2PM)'),
        ('Afternoon', 'Afternoon (2PM - 10PM)'),
        ('Night', 'Night (10PM - 6AM)'),
    ]
    
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, related_name='task_logs')
    task_type = models.CharField(max_length=20, choices=TASK_CHOICES)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    date = models.DateField(auto_now_add=True)
    completed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='completed_tasks')
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('admission', 'task_type', 'shift', 'date')
    
    def __str__(self):
        return f"{self.admission.patient.user.get_full_name()} - {self.shift}: {self.task_type}"


class NurseWaterIntake(models.Model):
    """Track nurse's own water intake per shift"""
    SHIFT_CHOICES = [
        ('Morning', 'Morning (6AM - 2PM)'),
        ('Afternoon', 'Afternoon (2PM - 10PM)'),
        ('Night', 'Night (10PM - 6AM)'),
    ]
    
    nurse = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='water_intakes', limit_choices_to={'role': 'Nurse'})
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    date = models.DateField(auto_now_add=True)
    glasses = models.IntegerField(default=0, help_text="Number of glasses consumed")
    logged_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('nurse', 'shift', 'date')
    
    def __str__(self):
        return f"{self.nurse.user.get_full_name()} - {self.shift}: {self.glasses} glasses"


class Medicine(models.Model):
    """Medicine database for pharmacy module"""
    MEDICINE_TYPES = [
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Syrup', 'Syrup'),
        ('Injection', 'Injection'),
        ('Ointment', 'Ointment'),
        ('Drops', 'Drops'),
        ('Inhaler', 'Inhaler'),
        ('Other', 'Other'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='medicines', null=True, blank=True)
    name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True)
    medicine_type = models.CharField(max_length=20, choices=MEDICINE_TYPES, default='Tablet')
    manufacturer = models.CharField(max_length=255, blank=True)
    
    # Stock management
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10, help_text="Minimum stock before reorder alert")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Availability
    is_available = models.BooleanField(default=True)
    is_external = models.BooleanField(default=False, help_text="Mark if medicine needs external purchase")
    
    # Details
    description = models.TextField(blank=True)
    dosage_instructions = models.TextField(blank=True, help_text="Standard dosage instructions")
    side_effects = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.medicine_type})"
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level


class PrescribedMedicine(models.Model):
    """Link medicines to prescriptions with detailed info"""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='prescribed_medicines')
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)
    medicine_name = models.CharField(max_length=255, help_text="Name of medicine (if not in DB)")
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet")
    frequency = models.CharField(max_length=100, help_text="e.g., Twice daily after meals")
    duration = models.CharField(max_length=100, help_text="e.g., 7 days")
    instructions = models.TextField(blank=True)
    is_external_purchase = models.BooleanField(default=False, help_text="Needs to be purchased externally")
    is_dispensed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.prescription.appointment.patient.user.get_full_name()}"


class InjectionSchedule(models.Model):
    """Track injection schedules for admitted patients"""
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, related_name='injections')
    medicine_name = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()
    is_given = models.BooleanField(default=False)
    given_at = models.DateTimeField(null=True, blank=True)
    given_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Nurse'})
    notes = models.TextField(blank=True)
    
    def __str__(self):
        status = "Given" if self.is_given else "Pending"
        return f"{self.medicine_name} - {status}"


class PatientMonitoringLog(models.Model):
    """Nurse monitoring panel logs"""
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, related_name='monitoring_logs')
    nurse = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Nurse'})
    
    # Monitoring details
    log_time = models.DateTimeField(auto_now_add=True)
    vitals = models.TextField(blank=True, help_text="BP, Pulse, Temperature, etc.")
    medicine_given = models.BooleanField(default=False)
    medicines_given_details = models.TextField(blank=True)
    injection_given = models.BooleanField(default=False)
    injection_details = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.admission.patient.user.get_full_name()} - {self.log_time.strftime('%Y-%m-%d %H:%M')}"


class Ambulance(models.Model):
    """Ambulance management"""
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('On Call', 'On Call'),
        ('Maintenance', 'Maintenance'),
        ('Offline', 'Offline'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='ambulances')
    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=50, default='Basic Life Support')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    
    # Driver information
    driver_name = models.CharField(max_length=255)
    driver_phone = models.CharField(max_length=15)
    driver_license = models.CharField(max_length=100, blank=True)
    
    # Equipment
    equipment_list = models.TextField(blank=True, help_text="List of medical equipment on board")
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    
    # Current assignment
    current_assignment = models.ForeignKey(PatientAdmission, on_delete=models.SET_NULL, null=True, blank=True, related_name='ambulance')
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.vehicle_number} - {self.status}"


class AmbulanceCall(models.Model):
    """Track ambulance emergency calls"""
    CALL_TYPES = [
        ('Hospital Request', 'Hospital Request'),
        ('Ambulance Alert', 'Ambulance Alert'),
        ('Patient Transfer', 'Patient Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Dispatched', 'Dispatched'),
        ('On Scene', 'On Scene'),
        ('Transporting', 'Transporting'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='ambulance_calls')
    ambulance = models.ForeignKey(Ambulance, on_delete=models.SET_NULL, null=True, blank=True)
    call_type = models.CharField(max_length=20, choices=CALL_TYPES)
    
    # Patient/Location details
    patient_name = models.CharField(max_length=255)
    pickup_location = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True)
    emergency_type = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    called_at = models.DateTimeField(auto_now_add=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True)
    
    # Alarm acknowledgment
    alarm_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.call_type} - {self.patient_name} - {self.status}"


class PersistentAlarm(models.Model):
    """Persistent alarm system for emergencies"""
    ALARM_TYPES = [
        ('Emergency', 'Emergency'),
        ('Ambulance', 'Ambulance'),
        ('Critical Patient', 'Critical Patient'),
        ('System', 'System'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='alarms')
    alarm_type = models.CharField(max_length=20, choices=ALARM_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects (polymorphic-like)
    emergency_case = models.ForeignKey(EmergencyCase, on_delete=models.CASCADE, null=True, blank=True)
    ambulance_call = models.ForeignKey(AmbulanceCall, on_delete=models.CASCADE, null=True, blank=True)
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alarms')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alarm_type}: {self.title}"


class EnhancedEmergencyCase(models.Model):
    """Extended emergency case with type and room assignment"""
    EMERGENCY_TYPES = [
        ('Accident', 'Accident'),
        ('Heart Attack', 'Heart Attack'),
        ('Organ Transplant', 'Organ Transplant'),
        ('Stroke', 'Stroke'),
        ('General', 'General'),
    ]
    
    # Link to original emergency case
    original_case = models.OneToOneField(EmergencyCase, on_delete=models.CASCADE, related_name='enhanced')
    
    # New fields
    emergency_type = models.CharField(max_length=20, choices=EMERGENCY_TYPES, default='General')
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    room_number = models.CharField(max_length=50, blank=True)
    
    # Auto-assigned specialist
    assigned_specialist = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='specialist_emergencies')
    
    # Assigned nurses (minimum 4)
    assigned_nurses = models.ManyToManyField(Staff, blank=True, related_name='emergency_cases', limit_choices_to={'role': 'Nurse'})
    
    # Alarm status
    alarm_active = models.BooleanField(default=True)
    alarm_acknowledged = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Enhanced: {self.original_case.patient_name} - {self.emergency_type}"
    
    def auto_assign_specialist(self):
        """Auto-assign specialist based on emergency type"""
        hospital = self.original_case.hospital
        
        specialty_map = {
            'Accident': 'Orthopedics',
            'Heart Attack': 'Cardiology',
            'Organ Transplant': 'Transplant Surgery',
            'Stroke': 'Neurology',
            'General': 'Emergency',
        }
        
        target_specialty = specialty_map.get(self.emergency_type, 'Emergency')
        
        # Find available doctor with matching specialty
        doctors = Doctor.objects.filter(
            hospital=hospital,
            department__icontains=target_specialty,
            available=True
        )
        
        if doctors.exists():
            self.assigned_specialist = doctors.first()
            self.save()
            return self.assigned_specialist
        
        # Fallback to any available emergency doctor
        emergency_docs = Doctor.objects.filter(
            hospital=hospital,
            department='Emergency',
            available=True
        )
        
        if emergency_docs.exists():
            self.assigned_specialist = emergency_docs.first()
            self.save()
            return self.assigned_specialist
        
        return None
    
    def auto_assign_nurses(self):
        """Auto-assign at least 4 nurses with lowest workload"""
        from django.db.models import F
        
        hospital = self.original_case.hospital
        
        # Get nurses with workload info, ordered by active patients (ascending)
        nurses = Staff.objects.filter(
            hospital=hospital,
            role='Nurse',
            user__is_active=True
        ).annotate(
            workload=models.Count('assigned_patients')
        ).order_by('workload')[:6]  # Get up to 6 to ensure we have at least 4 available
        
        assigned_count = 0
        for nurse in nurses:
            # Check if nurse workload allows more patients
            workload, created = NurseWorkload.objects.get_or_create(
                nurse=nurse,
                defaults={'max_patients': 5, 'active_patients': 0}
            )
            
            if workload.active_patients < workload.max_patients:
                self.assigned_nurses.add(nurse)
                workload.active_patients += 1
                workload.last_assigned = timezone.now()
                workload.save()
                assigned_count += 1
                
                if assigned_count >= 4:
                    break
        
        return assigned_count


class Payment(models.Model):
    """Online payment tracking for patient bills"""
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
        ('Wallet', 'Wallet'),
        ('Cash', 'Cash'),
    ]
    
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=255, blank=True)
    payment_gateway_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.amount} - {self.status}"


class AutoGeneratedCredentials(models.Model):
    """Track auto-generated credentials for new patients/users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auto_credentials')
    generated_username = models.CharField(max_length=150)
    generated_password = models.CharField(max_length=255)  # Store hashed or encrypted
    credentials_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to_email = models.EmailField()
    
    def __str__(self):
        return f"Credentials for {self.user.username}"


class DischargeSummary(models.Model):
    """Discharge summary for admitted patients"""
    admission = models.OneToOneField(PatientAdmission, on_delete=models.CASCADE, related_name='discharge_summary')
    discharge_date = models.DateTimeField(auto_now_add=True)
    discharged_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Summary details
    admission_diagnosis = models.TextField()
    final_diagnosis = models.TextField()
    treatment_given = models.TextField()
    surgery_procedures = models.TextField(blank=True)
    
    # Condition at discharge
    condition_at_discharge = models.TextField()
    follow_up_instructions = models.TextField()
    medications_on_discharge = models.TextField()
    
    # Restrictions
    activity_restrictions = models.TextField(blank=True)
    diet_instructions = models.TextField(blank=True)
    warning_signs = models.TextField(blank=True)
    
    follow_up_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Discharge Summary - {self.admission.patient.user.get_full_name()}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class InsuranceProvider(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name


class InsurancePolicy(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_policies')
    provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=100)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.policy_number}"


class InsuranceClaim(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    admission = models.ForeignKey(PatientAdmission, on_delete=models.CASCADE)
    provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE)
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Claim {self.id} - {self.patient.user.get_full_name()}"


class FamilyMember(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=50, choices=[
        ('Spouse', 'Spouse'),
        ('Child', 'Child'),
        ('Parent', 'Parent'),
        ('Guardian', 'Guardian')
    ])
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ])

    def __str__(self):
        return f"{self.full_name} ({self.relationship}) - {self.patient.user.get_full_name()}"


class HealthWalletItem(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='health_wallet')
    item_type = models.CharField(max_length=20, choices=[
        ('Prescription', 'Prescription'),
        ('LabReport', 'Lab Report'),
        ('Vaccination', 'Vaccination'),
        ('DischargeSummary', 'Discharge Summary'),
        ('Radiology', 'Radiology Report')
    ])
    file = models.FileField(upload_to='health_wallet/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    share_token = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.patient.user.get_full_name()}"


class WearableData(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wearable_data')
    data_type = models.CharField(max_length=50, choices=[
        ('HeartRate', 'Heart Rate'),
        ('BloodPressure', 'Blood Pressure'),
        ('Sleep', 'Sleep'),
        ('Activity', 'Activity')
    ])
    value = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, blank=True)
    recorded_at = models.DateTimeField()
    synced_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.data_type} - {self.patient.user.get_full_name()}"
