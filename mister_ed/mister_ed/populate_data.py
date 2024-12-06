# populate_data.py
import os
import django
import random
from datetime import datetime, timedelta
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from mister_ed.models import Clinic, Doctor, Service, Schedule, ED, MedicalStaff, Admin

# Generate random lat/lng coordinates for the Victoria, BC region
def generate_random_lat_lng():
    lat = random.uniform(48.4, 48.5)
    lng = random.uniform(-123.4, -123.3)
    return lat, lng

# Function to generate random triage data
def generate_random_triage():
    severe_symptoms = random.sample(['Chest pain', 'Severe bleeding', 'Unconscious'], k=random.randint(0, 2))
    symptoms = random.sample(['Fever', 'Headache', 'Cough', 'Nausea'], k=random.randint(1, 3))
    duration = random.choice(['Less than a day', '1-3 days', 'More than 3 days'])
    specific_symptoms = {
        symptom: random.sample(['High', 'Persistent', 'Sudden'], k=random.randint(0, 2))
        for symptom in symptoms
    }
    return {
        "severeSymptoms": severe_symptoms,
        "symptoms": symptoms,
        "duration": duration,
        "specificSymptoms": specific_symptoms
    }

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

# Create EDs with initial random load and queues
eds = []
for name, address in eds_data:
    lat, lng = generate_random_lat_lng()
    queue = [generate_random_triage() for _ in range(random.randint(5, 15))]  # Generate random queue
    ed = ED.objects.create(name=name, address=address, lat=lat, lng=lng, queue=queue)
    eds.append(ed)

# Create a User and MedicalStaff entry
medical_staff_users = [
    ("drsmith", "Dr. John Smith", "password123", "Doctor", "Cardiology", "drsmith@example.com", "555-1234"),
    ("nursejane", "Jane Doe", "password123", "Nurse", "Emergency Medicine", "nursejane@example.com", "555-5678"),
]

for username, name, password, role, specializing, email, contact in medical_staff_users:
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=name.split()[0],
        last_name=name.split()[1],
        email=email,
    )
    MedicalStaff.objects.create(
        user=user,
        name=name,
        role=role,
        specializing=specializing,
        contact_info=contact,
    )

# Create a User and Admin entry
admin_users = [
    ("adminuser", "Admin User", "password123", "adminuser@example.com", "555-9999"),
]

for username, name, password, email, contact in admin_users:
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=name.split()[0],
        last_name=name.split()[1],
        email=email,
    )
    Admin.objects.create(
        user=user,
        name=name,
        phone_number=contact,
    )

# List of Doctors with specialties
doctors_data = [
    ('Dr. Sarah Lee', 'Cardiologist'),
    ('Dr. Emily Wong', 'Dermatologist'),
    ('Dr. Michael Green', 'Orthopedic Surgeon'),
    ('Dr. Nancy Brown', 'Pediatrician'),
    ('Dr. Alex Taylor', 'Neurologist'),
]

# Create doctors
doctors = []
for name, specialty in doctors_data:
    doctor = Doctor.objects.create(name=name, specialty=specialty)
    doctors.append(doctor)

# List of Services
services_data = [
    ('Heart Surgery', doctors[0]),  # Dr. Sarah Lee
    ('Skin Check', doctors[1]),     # Dr. Emily Wong
    ('Knee Surgery', doctors[2]),   # Dr. Michael Green
    ('Child Checkup', doctors[3]),  # Dr. Nancy Brown
    ('Brain Scan', doctors[4]),     # Dr. Alex Taylor
]

# Create services
services = []
for service_name, doctor in services_data:
    service = Service.objects.create(service_name=service_name, doctor=doctor)
    services.append(service)

# Function to generate schedules
def generate_schedules(doctor, clinic, service, num_weeks=4):
    start_date = datetime.today()
    days_of_week = [0, 2, 4]  # Monday, Wednesday, Friday

    for week in range(num_weeks):
        available_day = random.choice(days_of_week)
        date = (start_date + timedelta(days=(week * 7 + available_day))).date()
        time_slots = ['09:00', '10:00', '11:00']
        for time_str in time_slots:
            time = datetime.strptime(time_str, '%H:%M').time()
            is_booked = random.choice([True, False])
            Schedule.objects.create(
                doctor=doctor,
                clinic=clinic,
                available_date=date,
                available_time=time,
                service=service,
                is_booked=is_booked,
            )

# Generate schedules for clinics
for doctor in doctors:
    doctor_services = Service.objects.filter(doctor=doctor)
    for service in doctor_services:
        clinic = random.choice(clinics)
        generate_schedules(doctor, clinic, service)

print("Database populated with clinics, emergency departments, medical staff, admin users, doctors, services, schedules, and ED queues.")
