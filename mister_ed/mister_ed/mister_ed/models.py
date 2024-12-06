from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse

# Patient model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    patient_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='Phone number must be exactly 10 digits.')]
    )
    address = models.CharField(max_length=100, null=False, blank=False, default='')
    # Added latitude and longitude fields
    lat = models.FloatField(null=False, blank=True, default=48.401936761021915)
    lng = models.FloatField(null=False, blank=True, default=-123.34136076541516)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Clinic model
class Clinic(models.Model):
    clinic_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    lat = models.FloatField(null=False, blank=False)
    lng = models.FloatField(null=False, blank=False)

    def __str__(self):
        return self.name
    
class Doctor(models.Model):
    doctor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    specialty = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.name
    
class Service(models.Model):
    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=255, null=False, blank=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.service_name} by {self.doctor.name}'
    
# ED (Emergency Department) model
class ED(models.Model):
    ed_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False, default='')
    lat = models.FloatField(null=False, blank=False)
    lng = models.FloatField(null=False, blank=False)
    queue = models.JSONField(default=list)  # Default to an empty list for the queue

    def __str__(self):
        return f'{self.name}'


# ED Capacity model
class EDCapacity(models.Model):
    ed_capacity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ed = models.ForeignKey(ED, on_delete=models.CASCADE)
    current_capacity = models.IntegerField(null=False, default=0, blank=False)
    max_capacity = models.IntegerField(null=False, default=0, blank=False)
    wait_time_estimate = models.TimeField(blank=True)

# Admin model
class Admin(models.Model):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=255, null=False, blank=False)
    phone_number = models.TextField(max_length=255, null=False, blank=False)

# Severity Level model
class SeverityLevel(models.Model):
    severity_level_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    priority = models.IntegerField()

# Triage Criteria model
class TriageCriteria(models.Model):
    triage_criteria_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    severity_level = models.ForeignKey(SeverityLevel, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

# Medical Staff model
class MedicalStaff(models.Model):
    staff_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    specializing = models.CharField(max_length=255)
    contact_info = models.TextField()

# Schedule model
class Schedule(models.Model):
    is_virtual = models.BooleanField(default=False)
    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    available_date = models.DateField()
    available_time = models.TimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.service.service_name} on {self.available_date} at {self.available_time}'

# Assessment model
class Assessment(models.Model):
    assessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    severity_level = models.ForeignKey(SeverityLevel, on_delete=models.CASCADE)
    recommended_action = models.TextField()
    assessment_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    staff = models.ForeignKey(MedicalStaff, on_delete=models.CASCADE)

# Patient Data model
class PatientData(models.Model):
    patient_data_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medical_history = models.TextField()
    current_symptoms = models.TextField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

# Appointment model
class Appointment(models.Model):
    appointment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Appointment for {self.user.username} with {self.schedule.service.service_name} on {self.schedule.available_date} at {self.schedule.available_time}'

# Notification model
class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    date_time = models.DateTimeField()
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE)
