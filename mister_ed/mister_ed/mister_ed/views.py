# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .models import Schedule, Appointment, Patient
from django.urls import reverse
from django.views.decorators.cache import cache_page
from math import radians, cos, sin, sqrt, atan2
import random
import logging
import json
from time import sleep

logger = logging.getLogger(__name__)

@login_required(login_url="/login")
def home(request):
    return render(request, 'home/home.html')

# @login_required(login_url="/login") 
# def triage(request):
#     return render(request, 'triage/triage.html')

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login") 
def triage(request):
    if request.method == 'POST':
        # Get the triage data from POST
        severeSymptoms = json.loads(request.POST.get('severeSymptoms', '[]'))
        symptoms = json.loads(request.POST.get('symptoms', '[]'))
        duration = request.POST.get('duration', '')
        specificSymptoms = json.loads(request.POST.get('specificSymptoms', '{}'))

        # Map duration to numerical value
        durationScore = 0
        if duration == 'Less than a day':
            durationScore = 1
        elif duration == '1-3 days':
            durationScore = 2
        elif duration == 'More than 3 days':
            durationScore = 3

        # Calculate severity based on severeSymptoms
        severity = 5 if len(severeSymptoms) > 0 else 0

        # Calculate symptoms score
        symptomsScore = len(symptoms)

        # Calculate priorityScore
        priorityScore = severity * 0.5 + symptomsScore * 0.3 + durationScore * 0.2

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

        print('Triage data received:', {
            'severeSymptoms': severeSymptoms,
            'symptoms': symptoms,
            'specificSymptoms': specificSymptoms,
            'duration': duration,
            'priorityScore': priorityScore,
            'recommended_action': recommended_action
        })  # Debugging output
        
        return render(request, 'selection/options.html', context)
    else:
        return render(request, 'triage/triage.html')


def resources(request):
    resources = [
        {
            "title": "Guide to Healthy Living",
            "link": "/resources/healthy-living",
            "description": "Learn the basics of maintaining a balanced and healthy lifestyle with daily tips.",
            "category": "Lifestyle",
            "icon": "fa-heart"
        },
        {
            "title": "Understanding Mental Health",
            "link": "/resources/mental-health",
            "description": "A comprehensive overview of mental health, including resources for support.",
            "category": "Mental Health",
            "icon": "fa-brain"
        },
        {
            "title": "Nutrition for All Ages",
            "link": "/resources/nutrition",
            "description": "Guidelines and tips for a nutritious diet suitable for all age groups.",
            "category": "Nutrition",
            "icon": "fa-apple-alt"
        },
        {
            "title": "Exercise Essentials",
            "link": "/resources/exercise-essentials",
            "description": "Get started with a beginner-friendly exercise routine and fitness tips.",
            "category": "Fitness",
            "icon": "fa-dumbbell"
        },
        {
            "title": "Stress Management Techniques",
            "link": "/resources/stress-management",
            "description": "Discover effective ways to manage stress and improve mental well-being.",
            "category": "Mental Health",
            "icon": "fa-smile"
        },
        {
            "title": "Healthy Eating on a Budget",
            "link": "/resources/eating-on-budget",
            "description": "Tips and tricks to eat healthy without breaking the bank.",
            "category": "Nutrition",
            "icon": "fa-leaf"
        }
    ]
    return render(request, 'home/resources.html', {'resources': resources})

@cache_page(60 * 15)
@login_required
def appointment_list(request):
    try:
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
    except Schedule.DoesNotExist:
        logger.error("Schedule data unavailable")
        return render(request, 'errors/no_appointments.html', status=404)
    except Exception as e:
        logger.error(f"Unknown error in appointment_list: {str(e)}")
        return render(request, 'errors/500.html', status=500)

@login_required
def book_appointment(request, schedule_id):
    max_retries = 3
    schedule = Schedule.objects.get(schedule_id=schedule_id)
    
    if request.method == 'POST':
        for attempt in range(max_retries):
            try:
                schedule.is_booked = True
                schedule.save()
                
                appointment = Appointment.objects.create(
                    user=request.user,
                    schedule=schedule
                )

                return render(request, 'selection/booking_confirmation.html', {'appointment': appointment})
            except Exception as e:
                logger.error(f"Booking attempt {attempt + 1} failed: {e}")
                sleep(1)  # Brief delay before retry
        return render(request, 'errors/booking_failed.html')
    
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

def healthy_living(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Guide to Healthy Living',
        'content': 'Just eat your vegetables... even the ones that don’t taste like candy!',
    })

def mental_health(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Mental Health Awareness',
        'content': 'If at first you don’t succeed, try doing it the way your therapist told you!',
    })

def nutrition(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Nutrition for All Ages',
        'content': 'Eat a balanced diet... by balancing your dessert with your salad!',
    })

def exercise_essentials(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Exercise Essentials',
        'content': 'You don’t have to run a marathon; just jog to the fridge and back a few times!',
    })

def stress_management(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Stress Management Techniques',
        'content': 'When life gives you lemons, just add them to your drink and pretend everything’s fine!',
    })

def eating_on_budget(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Healthy Eating on a Budget',
        'content': 'Why pay for fancy superfoods when you can just sprinkle some kale on your pizza?',
    })

def resource_of_the_day(request):
    return render(request, 'home/article_detail.html', {
        'title': 'Resource of the Day',
        'content': 'If you can’t find the motivation to exercise, just wear workout clothes all day. It’s like working out without breaking a sweat!',
    })
