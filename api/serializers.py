"""
DRF serializers for the PHLM REST API.

These expose every core model so the Flutter mobile app can read and write the
full database. Field names use Django's snake_case convention so the Flutter
models' fromJson/toJson helpers map directly.

File/Image fields are read-only here (uploads go through multipart endpoints or
are set server-side); auto timestamps are also read-only.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core import models

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_hospital_admin', 'is_doctor', 'is_patient',
            'is_lab', 'is_pharmacy', 'is_staff_member',
        )


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hospital
        fields = '__all__'
        read_only_fields = ('id',)


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Doctor
        fields = '__all__'
        read_only_fields = ('id', 'image')


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Patient
        fields = '__all__'
        read_only_fields = ('id', 'age')


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Staff
        fields = '__all__'
        read_only_fields = ('id', 'image')


class LabWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabWorker
        fields = '__all__'
        read_only_fields = ('id', 'image')


class PharmacyWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PharmacyWorker
        fields = '__all__'
        read_only_fields = ('id', 'image')


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LeaveRequest
        fields = '__all__'
        read_only_fields = ('id', 'applied_at', 'reviewed_by', 'reviewed_at')


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)

    class Meta:
        model = models.Appointment
        fields = '__all__'
        read_only_fields = ('id', 'doctor_name', 'patient_name')


class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabReport
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_at', 'patient_uploaded_at',
                           'result_uploaded_at', 'reviewed_by',
                           'file', 'patient_upload', 'result_file')


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prescription
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class PrescribedMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PrescribedMedicine
        fields = '__all__'
        read_only_fields = ('id',)


class TestRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TestRequest
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reminder
        fields = '__all__'
        read_only_fields = ('id',)


class DailyHealthStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DailyHealthStatus
        fields = '__all__'
        read_only_fields = ('id',)


class StaffHealthStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StaffHealthStatus
        fields = '__all__'
        read_only_fields = ('id',)


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ward
        fields = '__all__'
        read_only_fields = ('id',)


class PatientAdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PatientAdmission
        fields = '__all__'
        read_only_fields = ('id', 'admission_date', 'discharge_date')


class NurseWorkloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NurseWorkload
        fields = '__all__'
        read_only_fields = ('id', 'last_assigned')


class PatientWaterIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PatientWaterIntake
        fields = '__all__'
        read_only_fields = ('id', 'recorded_at')


class NurseTaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NurseTaskLog
        fields = '__all__'
        read_only_fields = ('id', 'completed_at')


class NurseWaterIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NurseWaterIntake
        fields = '__all__'
        read_only_fields = ('id', 'logged_at')


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Medicine
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class InjectionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InjectionSchedule
        fields = '__all__'
        read_only_fields = ('id', 'given_at')


class PatientMonitoringLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PatientMonitoringLog
        fields = '__all__'
        read_only_fields = ('id', 'log_time')


class AmbulanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ambulance
        fields = '__all__'
        read_only_fields = ('id',)


class AmbulanceCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AmbulanceCall
        fields = '__all__'
        read_only_fields = ('id', 'called_at', 'dispatched_at',
                           'arrived_at', 'completed_at', 'acknowledged_at')


class EmergencyCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmergencyCase
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class LabTestReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabTestReference
        fields = '__all__'
        read_only_fields = ('id',)


class PersistentAlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersistentAlarm
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'acknowledged_at')


class EnhancedEmergencyCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnhancedEmergencyCase
        fields = '__all__'
        read_only_fields = ('id',)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'completed_at')


class AutoGeneratedCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AutoGeneratedCredentials
        fields = '__all__'
        read_only_fields = ('id', 'sent_at')


class DischargeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DischargeSummary
        fields = '__all__'
        read_only_fields = ('id', 'discharge_date')


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuditLog
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')


class InsuranceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InsuranceProvider
        fields = '__all__'
        read_only_fields = ('id',)


class InsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InsurancePolicy
        fields = '__all__'
        read_only_fields = ('id',)


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InsuranceClaim
        fields = '__all__'
        read_only_fields = ('id', 'submitted_at', 'processed_at')


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FamilyMember
        fields = '__all__'
        read_only_fields = ('id',)


class HealthWalletItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HealthWalletItem
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_at', 'share_token', 'file')


class WearableDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WearableData
        fields = '__all__'
        read_only_fields = ('id', 'synced_at')


class WorkLogSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = models.WorkLog
        fields = (
            'id',
            'doctor',
            'doctor_name',
            'date',
            'start_time',
            'end_time',
            'duration_hours',
        )
        read_only_fields = ('id', 'date', 'start_time')

    def get_duration_hours(self, obj):
        return obj.duration()

