from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import RegexValidator

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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Clinic model
class Clinic(models.Model):
    clinic_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField(max_length=255, null=False, blank=False)

# ED (Emergency Department) model
class ED(models.Model):
    ed_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False, default='')

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
    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(MedicalStaff, on_delete=models.CASCADE)
    date = models.DateField()
    shift = models.CharField(max_length=255)

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
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    date_time = models.DateTimeField()

# Notification model
class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    date_time = models.DateTimeField()
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', default='profile_photos/default.jpg')
    def __str__(self):
        return self.user.username