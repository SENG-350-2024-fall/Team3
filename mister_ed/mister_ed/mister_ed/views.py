# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .models import Schedule, Appointment, Patient
from django.urls import reverse
from math import radians, cos, sin, sqrt, atan2
import random

@login_required(login_url="/login")
def home(request):
    return render(request, 'home/home.html')

def triage(request):
    if request.method == 'POST':
        # Get the triage data from POST
        severity = int(request.POST.get('severity', 0))
        symptoms = int(request.POST.get('symptoms', 0))
        duration = int(request.POST.get('duration', 0))
        additional = request.POST.get('additional', '')

        # Calculate priorityScore
        priorityScore = severity * 0.5 + symptoms * 0.3 + duration * 0.2

        # Determine the recommended action based on priorityScore
        if priorityScore < 2:
            recommended_action = 'No immediate action required'
            options = ['Virtual Meeting']
        elif priorityScore < 5:
            recommended_action = 'Consider visiting a clinic'
            options = ['Clinic Visit', 'Virtual Meeting']
        else:
            recommended_action = 'Immediate medical attention required'
            options = ['Visit to ED', 'Paramedic Visit']

        context = {
            'recommended_action': recommended_action,
            'options': options,
        }

        return render(request, 'selection/options.html', context)
    else:
        return redirect('home')

@login_required
def appointment_list(request):
    # Handle the POST request if selecting from options
    if request.method == 'POST':
        selected_option = request.POST.get('selected_option', '')
        if selected_option != 'Clinic Visit':
            # Redirect to home if the selected option is not 'Clinic Visit'
            return redirect('home')

    # Proceed to fetch and display available appointments for GET requests or valid POST requests
    patient = request.user.patient
    client_lat = patient.lat
    client_lng = patient.lng

    schedules = Schedule.objects.filter(is_booked=False)

    def haversine(lat1, lng1, lat2, lng2):
        R = 6371  # Earth radius in kilometers
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    schedule_list = []
    for schedule in schedules:
        clinic = schedule.clinic
        distance = haversine(client_lat, client_lng, clinic.lat, clinic.lng)
        schedule.distance = distance
        schedule_list.append(schedule)

    schedule_list.sort(key=lambda x: (x.available_date, x.available_time, x.distance))

    context = {
        'schedules': schedule_list,
    }
    return render(request, 'selection/appointment_list.html', context)


@login_required
def book_appointment(request, schedule_id):
    schedule = Schedule.objects.get(schedule_id=schedule_id)
    if request.method == 'POST':
        # Confirm booking
        schedule.is_booked = True
        schedule.save()

        # Create an Appointment instance
        appointment = Appointment.objects.create(
            user=request.user,
            schedule=schedule
        )

        return render(request, 'selection/booking_confirmation.html', {'appointment': appointment})
    else:
        return render(request, 'selection/booking_confirm.html', {'schedule': schedule})

def login_view(request):
    return render(request, 'registration/login.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('/home')
    elif request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assign random latitude and longitude to the patient (Victoria, BC area)
            patient = user.patient
            patient.lat = random.uniform(48.4, 48.5)
            patient.lng = random.uniform(-123.4, -123.3)
            patient.save()
            return redirect('/home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})
