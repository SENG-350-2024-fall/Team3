import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from mister_ed.models import Doctor, Clinic, Service, Schedule

# Function to generate virtual meetings for doctors and their services
def add_virtual_meetings(num_weeks=4):
    doctors = Doctor.objects.all()
    virtual_clinic_name = "Virtual Clinic"
    
    # Check if a virtual clinic exists, if not, create one
    virtual_clinic, created = Clinic.objects.get_or_create(
        name=virtual_clinic_name,
        defaults={
            'address': 'Online',
            'lat': 0.0,  # Virtual clinic doesn't require coordinates
            'lng': 0.0,
        }
    )
    
    start_date = datetime.today()
    days_of_week = [0, 2, 4]  # Monday, Wednesday, Friday
    
    for doctor in doctors:
        doctor_services = Service.objects.filter(doctor=doctor)
        for service in doctor_services:
            if "Virtual" not in service.service_name:
                continue  # Skip non-virtual services
            
            for week in range(num_weeks):
                available_day = random.choice(days_of_week)
                date = (start_date + timedelta(days=(week * 7 + available_day))).date()
                time_slots_choices = [['09:00', '10:00'], ['14:00'], ['11:00', '12:00']]
                time_slots = random.choice(time_slots_choices)
                
                for time_str in time_slots:
                    time = datetime.strptime(time_str, '%H:%M').time()
                    Schedule.objects.create(
                        doctor=doctor,
                        clinic=virtual_clinic,
                        available_date=date,
                        available_time=time,
                        service=service,
                        is_virtual=True,
                        is_booked=False
                    )
    print(f"Virtual meetings added successfully for {len(doctors)} doctors and their services.")

# Add virtual meetings
add_virtual_meetings()
