import sqlite3
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime

# Haversine formula to calculate the distance between two lat/lng coordinates
def haversine(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # Distance in kilometers

# Define the Client class with attributes like location and required service
class Client:
    def __init__(self, name, lat, lng, required_service):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.required_service = required_service

# Function to find the top 3 best appointments
def find_best_appointments(client):
    # Connect to the SQLite database
    conn = sqlite3.connect('Database/clinic_appointments_realistic.db')
    cursor = conn.cursor()

    # Step 1: Fetch all appointments that match the required service
    query = '''
        SELECT Clinic.name, Clinic.lat, Clinic.lng, Schedule.available_date, Schedule.available_time, Doctor.name, Service.service_name
        FROM Schedule
        JOIN Clinic ON Schedule.clinic_id = Clinic.id
        JOIN Doctor ON Schedule.doctor_id = Doctor.id
        JOIN Service ON Schedule.service_id = Service.id
        WHERE Service.service_name = ?
    '''
    cursor.execute(query, (client.required_service,))
    appointments = cursor.fetchall()

    # Step 2: Calculate the distance between the client and each clinic
    appointment_data = []
    for appointment in appointments:
        clinic_name, clinic_lat, clinic_lng, available_date, available_time, doctor_name, service_name = appointment
        distance = haversine(client.lat, client.lng, clinic_lat, clinic_lng)
        
        # Combine the appointment data with the calculated distance
        appointment_data.append({
            'clinic_name': clinic_name,
            'clinic_lat': clinic_lat,
            'clinic_lng': clinic_lng,
            'available_date': available_date,
            'available_time': available_time,
            'doctor_name': doctor_name,
            'service_name': service_name,
            'distance': distance
        })

    # Step 3: Sort the appointments by date/time first, then by distance
    appointment_data.sort(key=lambda x: (x['available_date'], x['available_time'], x['distance']))

    # Step 4: Return the top 3 appointments
    top_appointments = appointment_data[:3]

    # Close the database connection
    conn.close()

    return top_appointments

# Example usage
if __name__ == "__main__":
    # Create a client instance with their location and required service
    client = Client(name="John Doe", lat=48.4284, lng=-123.3656, required_service="Consultation")

    # Find the best appointments for this client
    best_appointments = find_best_appointments(client)

    # Print the top 3 appointments
    print("Top 3 Best Appointments for:", client.name)
    for i, appointment in enumerate(best_appointments, 1):
        print(f"Option {i}:")
        print(f"  Clinic: {appointment['clinic_name']}")
        print(f"  Doctor: {appointment['doctor_name']}")
        print(f"  Service: {appointment['service_name']}")
        print(f"  Date: {appointment['available_date']}")
        print(f"  Time: {appointment['available_time']}")
        print(f"  Distance: {appointment['distance']:.2f} km")
        print()
