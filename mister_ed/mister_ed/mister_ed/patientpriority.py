from datetime import timedelta
from django.utils import timezone
from .models import Patient

# Define weight factors for each criterion
WEIGHTS = {
    'severity': 0.5,        # Severity is given the most importance
    'waiting_time': 0.3,    # Waiting time comes next
    'age': 0.1,             # Age has less importance
    'chronic_conditions': 0.05,  # Chronic conditions are considered slightly
    'emergency': 0.5        # Emergency situations get a high priority
}

def calculate_priority_score(patient):
    """
    Calculate the priority score for a patient based on weighted factors.
    """
    severity_score = patient.severity * WEIGHTS['severity']
    
    # Convert waiting time (in seconds) to minutes and apply weight
    waiting_minutes = patient.waiting_time.total_seconds() / 60
    waiting_time_score = min(waiting_minutes / 60, 1) * WEIGHTS['waiting_time']  # Cap the waiting score
    
    age_score = (100 - patient.age) / 100 * WEIGHTS['age']  # Younger patients prioritized for age
    chronic_condition_score = WEIGHTS['chronic_conditions'] if patient.chronic_conditions else 0
    emergency_score = WEIGHTS['emergency'] if patient.emergency else 0
    
    # Total weighted score
    total_score = severity_score + waiting_time_score + age_score + chronic_condition_score + emergency_score
    return total_score

def sort_patients_by_priority():
    # Fetch all patients
    patients = Patient.objects.all()
    
    # Calculate and assign a priority score to each patient
    patients_with_scores = [(patient, calculate_priority_score(patient)) for patient in patients]
    
    # Sort patients by priority score in descending order (higher score = higher priority)
    sorted_patients = sorted(patients_with_scores, key=lambda x: x[1], reverse=True)
    
    return [patient for patient, score in sorted_patients]

# Example view to display sorted patients
from django.shortcuts import render

def patient_list(request):
    sorted_patients = sort_patients_by_priority()
    return render(request, 'patient_list.html', {'patients': sorted_patients})
