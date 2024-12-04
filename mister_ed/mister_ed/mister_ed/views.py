# views.py

import os
import json
import openai
import logging
import random
from time import sleep
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from .forms import SignupForm
from .models import Schedule, Appointment, ED, Doctor, Service, Clinic, Patient
from django.core.exceptions import ObjectDoesNotExist
from math import radians, cos, sin, sqrt, atan2
from django.utils import timezone
from datetime import timedelta, time
from dotenv import load_dotenv
from .forms import ProfileForm

# Load environment variables and set OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
logger = logging.getLogger(__name__)

@login_required(login_url="/login")
def home(request):
    return render(request, 'home/home.html')

@login_required(login_url="/login")
def triage(request):
    if request.method == 'POST':
        # Retrieve data from POST request
        severeSymptoms = json.loads(request.POST.get('severeSymptoms', '[]'))
        symptoms = json.loads(request.POST.get('symptoms', '[]'))
        duration = request.POST.get('duration', '')
        specificSymptoms = json.loads(request.POST.get('specificSymptoms', '{}'))

        # Generate prompt for the API
        user_prompt = generate_prompt(severeSymptoms, symptoms, specificSymptoms, duration)

        # Print the data for debugging
        print('Triage data received:', {
            'severeSymptoms': severeSymptoms,
            'symptoms': symptoms,
            'specificSymptoms': specificSymptoms,
            'duration': duration,
            'prompt': user_prompt
        })

        try:
            # Call the OpenAI API using ChatCompletion
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            openai.api_key = OPENAI_API_KEY

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a medical triage assistant. Based on the provided symptoms, "
                            "recommend appropriate medical actions: 'Paramedics', 'ED', 'Clinic', or 'Virtual Meeting'. "
                            'Provide the recommendations in a valid JSON array format using double quotes, e.g., ["ED", "Paramedics"]. '
                            "Do not include any additional text."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=150,
                temperature=0.0,
            )

            # Extract the assistant's reply
            assistant_reply = response.choices[0].message.content
            print("REPLY:", assistant_reply)

            # Parse the assistant's reply
            try:
                assistant_reply = assistant_reply.strip()
                recommended_actions = json.loads(assistant_reply)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Attempt to fix common issues
                assistant_reply = assistant_reply.replace("'", '"')
                try:
                    recommended_actions = json.loads(assistant_reply)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error after replacement: {e}")
                    return render(request, 'errors/500.html', status=500)

            context = {
                'recommended_action': 'Based on your symptoms, we recommend the following option(s):',
                'options': recommended_actions,
            }

            return render(request, 'selection/options.html', context)

        except Exception as e:
            # Handle errors
            print(f"Error calling OpenAI API: {e}")
            return render(request, 'errors/500.html', status=500)
    else:
        return render(request, 'triage/triage.html')

def generate_prompt(severeSymptoms, symptoms, specificSymptoms, duration):
    prompt = "Patient reports the following symptoms:\n"

    if severeSymptoms:
        prompt += "Severe symptoms:\n"
        for symptom in severeSymptoms:
            # Map the severe symptom codes to their descriptions if necessary
            symptom_description = symptom.replace('-', ' ').capitalize()
            prompt += f"- {symptom_description}\n"

    if symptoms:
        prompt += "Main symptoms:\n"
        for symptom in symptoms:
            symptom_description = symptom.replace('-', ' ').capitalize()
            prompt += f"- {symptom_description}\n"
            attributes = specificSymptoms.get(symptom, [])
            if attributes:
                prompt += "  Attributes:\n"
                for attribute in attributes:
                    attribute_description = attribute.replace('-', ' ').capitalize()
                    prompt += f"  - {attribute_description}\n"

    if duration:
        prompt += f"Duration: {duration}\n"

    prompt += (
        "\nBased on these symptoms, what medical action(s) should the patient take? "
        'Please respond with a JSON array of options from ["Paramedics", "ED", "Clinic", "Virtual Meeting"]. '
        "Do not include any additional text."
    )

    return prompt

def generate_random_coordinates():
    # Generate random coordinates around Victoria, BC
    lat = random.uniform(48.4, 48.5)  # Latitude range for Victoria, BC
    lng = random.uniform(-123.4, -123.3)  # Longitude range for Victoria, BC
    return lat, lng

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    elif request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally, log the user in after signup
            # login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return LoginView.as_view(template_name='registration/login.html')(request)

@login_required
def book_appointment(request, schedule_id):
    try:
        schedule = Schedule.objects.get(schedule_id=schedule_id)
    except ObjectDoesNotExist:
        # Handle schedule not found
        return render(request, 'errors/404.html', status=404)

    if schedule.is_booked:
        # Handle already booked case
        return render(request, 'selection/already_booked.html', {'schedule': schedule})

    if request.method == 'POST':
        schedule.is_booked = True
        schedule.save()
        appointment = Appointment.objects.create(
            user=request.user,
            schedule=schedule
        )
        return render(request, 'selection/booking_confirmation.html', {'appointment': appointment})
    else:
        return render(request, 'selection/booking_confirm.html', {'schedule': schedule})

@login_required
def virtual_meetings(request):
    available_schedules = Schedule.objects.filter(is_virtual=True, is_booked=False)
    return render(request, 'selection/virtual_meetings.html', {'schedules': available_schedules})

@login_required
def ed_locations(request):
    eds = ED.objects.all()
    return render(request, 'selection/ed_locations.html', {'eds': eds})

@cache_page(60 * 15)
@login_required
def appointment_list(request):
    try:
        # Handle the POST request if selecting from options
        if request.method == 'POST':
            selected_option = request.POST.get('selected_option', '')
            if selected_option == 'Clinic':
                pass
            elif selected_option == 'ED':
                return redirect('ed_locations')
            elif selected_option == 'Virtual Meeting':
                return redirect('virtual_meetings')
            else:
                return redirect('home')

        # Proceed to fetch and display available appointments for GET requests or valid POST requests
        patient = request.user.patient
        client_lat = patient.lat
        client_lng = patient.lng

        schedules = Schedule.objects.filter(is_booked=False)

        def haversine(lat1, lng1, lat2, lng2):
            if lat1 is None or lng1 is None or lat2 is None or lng2 is None:
                return float('inf')  # Return a large distance for missing coordinates
            R = 6371  # Earth radius in kilometers
            dlat = radians(lat2 - lat1)
            dlng = radians(lng2 - lng1)
            a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        schedule_list = []
        for schedule in schedules:
            clinic = schedule.clinic
            if clinic.lat is not None and clinic.lng is not None:
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
def resources(request):
    # Sample data for resources
    resources_data = [
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
    return render(request, 'home/resources.html', {'resources': resources_data})

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

def medical_records(request):
    records = [
        {"date": "2024-01-10", "diagnosis": "Flu", "treatment": "Rest and hydration"},
        {"date": "2024-03-15", "diagnosis": "Sprained Ankle", "treatment": "Physical therapy"},
        # Add more records as needed
    ]
    return render(request, "home/medical_records.html", {"records": records})

@login_required
def profile(request):
    user = request.user
    patient = user.patient  # Assuming OneToOneField relationship exists

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=patient)
        if form.is_valid():
            # Save Patient data
            form.save()
            # Save email to User model
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('profile')
    else:
        # Populate initial data with the email from the User model
        form = ProfileForm(instance=patient, initial={'email': user.email})
    
    return render(request, 'home/profile.html', {'form': form})