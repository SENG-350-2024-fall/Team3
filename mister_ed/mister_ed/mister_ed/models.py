from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    phone_number = models.CharField(null=False, max_length=10)
