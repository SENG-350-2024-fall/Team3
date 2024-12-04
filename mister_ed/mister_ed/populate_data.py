# populate_data.py
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from mister_ed.models import Clinic, Doctor, Service, Schedule, ED

# Generate random lat/lng coordinates for the Victoria, BC region
def generate_random_lat_lng():
    lat = random.uniform(48.4, 48.5)
    lng = random.uniform(-123.4, -123.3)
    return lat, lng

# List of Clinics in Victoria, BC with lat/lng coordinates
clinics_data = [
    ('Victoria General Hospital', '1 Hospital Way, Victoria, BC'),
    ('Royal Jubilee Hospital', '1952 Bay St, Victoria, BC'),
    ('Saanich Peninsula Hospital', '2166 Mt Newton X Rd, Saanichton, BC'),
    ('Island Health Urgent Care', '1234 Fort St, Victoria, BC'),
    ('Esquimalt Medical Clinic', '101 Esquimalt Rd, Victoria, BC'),
    ('Oak Bay Clinic', '222 Oak Bay Ave, Victoria, BC'),
]

# Create clinics
clinics = []
for name, address in clinics_data:
    lat, lng = generate_random_lat_lng()
    clinic = Clinic.objects.create(name=name, address=address, lat=lat, lng=lng)
    clinics.append(clinic)

# List of Emergency Departments
eds_data = [
    ('Victoria Regional ED', '15 Emergency Blvd, Victoria, BC'),
    ('Island Health Emergency Services', '200 Health Ave, Victoria, BC'),
    ('Peninsula General ED', '45 Peninsula Way, Saanichton, BC'),
    ('Downtown Victoria Emergency', '300 Main St, Victoria, BC'),
    ('Harborview ED', '25 Marine Dr, Victoria, BC'),
]

# Create EDs
eds = []
for name, address in eds_data:
    lat, lng = generate_random_lat_lng()
    ed = ED.objects.create(name=name, address=address, lat=lat, lng=lng)
    eds.append(ed)

# List of Doctors with specialties
doctors_data = [
    ('Dr. John Smith', 'General Practitioner'),
    ('Dr. Sarah Lee', 'Cardiologist'),
    ('Dr. Emily Wong', 'Dermatologist'),
    ('Dr. Michael Green', 'Orthopedic Surgeon'),
    ('Dr. Nancy Brown', 'Pediatrician'),
    ('Dr. Alex Taylor', 'Neurologist'),
    ('Dr. Samantha White', 'General Practitioner'),
]

# Create doctors
doctors = []
for name, specialty in doctors_data:
    doctor = Doctor.objects.create(name=name, specialty=specialty)
    doctors.append(doctor)

# List of Services
services_data = [
    ('Consultation', doctors[0]),  # Dr. John Smith
    ('Heart Surgery', doctors[1]),  # Dr. Sarah Lee
    ('Skin Check', doctors[2]),     # Dr. Emily Wong
    ('Knee Surgery', doctors[3]),   # Dr. Michael Green
    ('Child Checkup', doctors[4]),  # Dr. Nancy Brown
    ('Brain Scan', doctors[5]),     # Dr. Alex Taylor
    ('Consultation', doctors[6]),   # Dr. Samantha White
    ('Virtual Consultation', doctors[0]),  # Virtual option
]

# Create services
services = []
for service_name, doctor in services_data:
    service = Service.objects.create(service_name=service_name, doctor=doctor)
    services.append(service)

# Function to generate schedules with some booked and some available slots
def generate_schedules(doctor, clinic, service, num_weeks=4, is_virtual=False):
    start_date = datetime.today()
    days_of_week = [0, 2, 4]  # Monday, Wednesday, Friday

    for week in range(num_weeks):
        available_day = random.choice(days_of_week)
        date = (start_date + timedelta(days=(week * 7 + available_day))).date()
        time_slots_choices = [['09:00', '10:00'], ['14:00'], ['11:00', '12:00']]
        time_slots = random.choice(time_slots_choices)

        for time_str in time_slots:
            time = datetime.strptime(time_str, '%H:%M').time()
            is_booked = random.choice([True, False])
            Schedule.objects.create(
                doctor=doctor,
                clinic=clinic,
                available_date=date,
                available_time=time,
                service=service,
                is_virtual=is_virtual,
                is_booked=is_booked
            )

# Generate schedules for clinics
for doctor in doctors:
    doctor_services = Service.objects.filter(doctor=doctor)
    for service in doctor_services:
        clinic = random.choice(clinics)
        is_virtual = "Virtual" in service.service_name
        generate_schedules(doctor, clinic, service, is_virtual=is_virtual)

print("Database populated with clinics, emergency departments, doctors, services, and schedules.")
