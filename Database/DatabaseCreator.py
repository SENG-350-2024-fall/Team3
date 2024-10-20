import sqlite3
from random import randint, choice, uniform
from datetime import datetime, timedelta

# Create a connection to the database
conn = sqlite3.connect('Database/clinic_appointments_realistic.db')
cursor = conn.cursor()

# Drop tables if they exist to avoid conflicts in testing
cursor.execute('DROP TABLE IF EXISTS Clinic')
cursor.execute('DROP TABLE IF EXISTS Doctor')
cursor.execute('DROP TABLE IF EXISTS Service')
cursor.execute('DROP TABLE IF EXISTS Schedule')

# Create Clinic table with lat/lng instead of distance_from_client
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clinic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL
    )
''')

# Create Doctor table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Doctor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL
    )
''')

# Create Service table (each service offered by a doctor)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Service (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        doctor_id INTEGER NOT NULL,
        FOREIGN KEY (doctor_id) REFERENCES Doctor (id)
    )
''')

# Create Schedule table (when a doctor is available at a clinic)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        clinic_id INTEGER NOT NULL,
        available_date TEXT NOT NULL,
        available_time TEXT NOT NULL,
        service_id INTEGER NOT NULL,
        is_booked INTEGER DEFAULT 0,  -- New field to track if the appointment is booked
        FOREIGN KEY (doctor_id) REFERENCES Doctor (id),
        FOREIGN KEY (clinic_id) REFERENCES Clinic (id),
        FOREIGN KEY (service_id) REFERENCES Service (id)
    )
''')

# Generate random lat/lng coordinates for clinics in the Victoria, BC region
def generate_random_lat_lng():
    lat = uniform(48.4, 48.5)
    lng = uniform(-123.4, -123.3)
    return lat, lng

# Expanded list of Clinics in Victoria, BC with lat/lng coordinates
clinics = [
    ('Victoria General Hospital', '1 Hospital Way, Victoria, BC', *generate_random_lat_lng()),
    ('Royal Jubilee Hospital', '1952 Bay St, Victoria, BC', *generate_random_lat_lng()),
    ('Saanich Peninsula Hospital', '2166 Mt Newton X Rd, Saanichton, BC', *generate_random_lat_lng()),
    ('Island Health Urgent Care', '1234 Fort St, Victoria, BC', *generate_random_lat_lng()),
    ('Esquimalt Medical Clinic', '101 Esquimalt Rd, Victoria, BC', *generate_random_lat_lng()),
    ('Oak Bay Clinic', '222 Oak Bay Ave, Victoria, BC', *generate_random_lat_lng())
]

# Expanded list of Doctors with specialties
doctors = [
    ('Dr. John Smith', 'General Practitioner'),
    ('Dr. Sarah Lee', 'Cardiologist'),
    ('Dr. Emily Wong', 'Dermatologist'),
    ('Dr. Michael Green', 'Orthopedic Surgeon'),
    ('Dr. Nancy Brown', 'Pediatrician'),
    ('Dr. Alex Taylor', 'Neurologist'),
    ('Dr. Samantha White', 'General Practitioner')
]

# Expanded list of Services
services = [
    ('Consultation', 1),  # Dr. John Smith
    ('Heart Surgery', 2),  # Dr. Sarah Lee
    ('Skin Check', 3),  # Dr. Emily Wong
    ('Knee Surgery', 4),  # Dr. Michael Green
    ('Child Checkup', 5),  # Dr. Nancy Brown
    ('Brain Scan', 6),  # Dr. Alex Taylor
    ('Consultation', 7),  # Dr. Samantha White
    ('Minor Surgery', 1),  # Dr. John Smith
    ('Skin Biopsy', 3),  # Dr. Emily Wong
]

# Function to generate scarce schedules with some booked and some available slots
def generate_scarce_schedules(doctor_id, clinic_id, service_id, num_weeks=4):
    schedules = []
    # Sparse schedule: only 1-2 days per week, 1-2 slots per day
    start_date = datetime.today()
    days_of_week = ['Monday', 'Wednesday', 'Friday']
    
    for week in range(num_weeks):
        # Choose random days of the week for appointments
        available_day = choice(days_of_week)
        date = (start_date + timedelta(days=(week * 7 + days_of_week.index(available_day)))).strftime('%Y-%m-%d')
        
        # For each day, choose 1-2 time slots
        time_slots = choice([['09:00', '10:00'], ['14:00'], ['11:00', '12:00']])
        
        for time in time_slots:
            # Randomly mark some slots as booked (is_booked = 1) and some as available (is_booked = 0)
            is_booked = choice([0, 1])  # Randomly decide if the slot is booked or available
            schedules.append((doctor_id, clinic_id, date, time, service_id, is_booked))
    
    return schedules

# Expanded schedules for doctors at different clinics with different services
schedule_data = []
for doctor_id in range(1, len(doctors) + 1):
    # Assign different services for each doctor
    doctor_services = [s for s in services if s[1] == doctor_id]
    
    for service in doctor_services:
        clinic_id = choice(range(1, len(clinics) + 1))  # Assign to random clinic
        service_id = services.index(service) + 1  # Get the service ID
        # Generate realistic, scarce schedule for the doctor with the service
        schedule_data.extend(generate_scarce_schedules(doctor_id, clinic_id, service_id))

# Insert data into Clinic table (with lat/lng)
cursor.executemany('''
    INSERT INTO Clinic (name, address, lat, lng)
    VALUES (?, ?, ?, ?)
''', clinics)

# Insert data into Doctor table
cursor.executemany('''
    INSERT INTO Doctor (name, specialty)
    VALUES (?, ?)
''', doctors)

# Insert data into Service table
cursor.executemany('''
    INSERT INTO Service (service_name, doctor_id)
    VALUES (?, ?)
''', services)

# Insert scarce schedule data into Schedule table with `is_booked` field
cursor.executemany('''
    INSERT INTO Schedule (doctor_id, clinic_id, available_date, available_time, service_id, is_booked)
    VALUES (?, ?, ?, ?, ?, ?)
''', schedule_data)

# Commit and close
conn.commit()
conn.close()

print("Database updated with all time slots, including booked and available appointments.")
