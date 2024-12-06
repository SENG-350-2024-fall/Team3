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
from .models import Schedule, Appointment, ED, Doctor, Service, Clinic, Patient, MedicalStaff, User
from django.core.exceptions import ObjectDoesNotExist
from math import radians, cos, sin, sqrt, atan2
from django.utils import timezone
from datetime import timedelta, time
from dotenv import load_dotenv
from .forms import ProfileForm
from django.utils.timezone import now
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        print(f"User {user.username} logged in.")  # Debug statement
        if hasattr(user, 'medicalstaff'):
            print("Redirecting to medical staff dashboard.")  # Debug statement
            return reverse('medical_staff_dashboard')
        elif hasattr(user, 'admin'):
            print("Redirecting to admin dashboard.")  # Debug statement
            return reverse('admin_dashboard')
        print("Redirecting to home.")  # Debug statement
        return reverse('home')
    
    def post(self, request, *args, **kwargs):
        print(f"CSRF token in cookie: {request.COOKIES.get('csrftoken')}")
        print(f"CSRF token in POST: {request.POST.get('csrfmiddlewaretoken')}")
        return super().post(request, *args, **kwargs)
    
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
        additionalInfo = request.POST.get('additionalInfo', '').strip()
        
        # Generate prompt for the API
        user_prompt = generate_prompt(severeSymptoms, symptoms, specificSymptoms, duration, additionalInfo)
        
        # Print the data for debugging
        print('Triage data received:', {
            'severeSymptoms': severeSymptoms,
            'symptoms': symptoms,
            'specificSymptoms': specificSymptoms,
            'duration': duration,
            'additionalInfo': additionalInfo,
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

def generate_prompt(severeSymptoms, symptoms, specificSymptoms, duration, additionalInfo):
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

    if additionalInfo:
        prompt += f"Additional Information: {additionalInfo}\n"

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
    eds = ED.objects.all().order_by('queue')  # Optionally order by load (low to high)
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

    try:
        patient = user.patient
    except Patient.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    return render(request, 'home/profile.html', {'user': user, 'patient': patient})


@login_required
def get_ed_queue(request, ed_id):
    """
    Fetch the queue for a specific ED and return it as JSON.
    """
    try:
        ed = ED.objects.get(id=ed_id)
    except ED.DoesNotExist:
        return JsonResponse({"error": "ED not found"}, status=404)

    queue = ed.queue
    return JsonResponse({"queue": queue})


@login_required
def update_ed_queue(request):
    """
    Simulate queue movement for all EDs.
    Randomly adds or removes patients from each ED's queue.
    """
    eds = ED.objects.all()
    for ed in eds:
        # Randomly add a new patient
        if random.choice([True, False]):
            ed.queue.append(generate_random_triage())

        # Randomly remove a patient
        if ed.queue and random.choice([True, False]):
            ed.queue.pop(0)

        ed.save()

    return JsonResponse({"message": "ED queues updated successfully."})


def generate_random_triage():
    """
    Generate random triage data for a patient.
    """
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

@login_required
def ed_detail(request, ed_id):
    """
    Render a detailed view of an ED, including its queue information and the user's determined position in the queue.
    """
    try:
        ed = ED.objects.get(ed_id=ed_id)
    except ED.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    # Try to fetch the associated Patient object
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        # Log the error and return an informative message
        logger.error(f"Patient data not found for user: {request.user.username}")
        return render(request, 'errors/404.html', {"message": "Patient data not found. Please complete your profile."})

    # Generate triage data for the user
    triage_data = generate_random_triage()

    # Determine the user's position in the queue
    user_position = -1
    try:
        chat_prompt = generate_placement_prompt(triage_data, ed)
        openai_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a triage assistant for emergency departments."},
                {"role": "user", "content": chat_prompt},
            ],
            max_tokens=100,
        )
        assistant_reply = openai_response.choices[0].message.content.strip()
        user_position = int(assistant_reply)
        user_position = max(0, min(user_position, len(ed.queue)))  # Clamp to valid range
        request.session['user_position'] = user_position
    except Exception as e:
        logger.error(f"Error calling ChatGPT API for placement: {e}")

    # Calculate total queue load
    capacity = 100  # Assuming maximum capacity of 100 users
    load_percentage = min(len(ed.queue) / capacity * 100, 100)

    context = {
        "ed": ed,
        "queue": ed.queue,
        "queue_length": len(ed.queue),
        "user_position": user_position if user_position != -1 else "Error determining position",
        "load_percentage": int(load_percentage),
    }
    return render(request, 'selection/ed_detail.html', context)


def generate_placement_prompt(triage_data, ed):
    """
    Generate a prompt to ask ChatGPT where the user should be placed in the queue.
    """
    queue_data = "\n".join([str(item) for item in ed.queue])
    prompt = (
        f"The current queue at {ed.name} is:\n{queue_data}\n"
        "A new patient has the following triage data:\n"
        f"{json.dumps(triage_data, indent=2)}\n"
        "Based on the patient's severity and symptoms, where should they be placed in the queue? "
        "Respond with the position as an integer (e.g., 0 for the front, 1 for second, etc.). DO NOT RESPOND WITH ANYTHING ELSE JUST THE NUMBER"
        "Additionally, to keep it more interesting, feel free to be a bit more lenient with the placement, so its not in the very front or the very end."
        f"If there are no users, output 0, else find output a value between 0 (start of the queue) and {len(ed.queue)} (endof the queue)."
    )
    return prompt


@login_required
def ed_locations(request):
    """
    Displays EDs with their respective load percentages.
    """
    eds = ED.objects.all()
    context = {
        "eds": eds
    }
    return render(request, 'selection/ed_locations.html', context)


@login_required
def update_ed_loads(request):
    """
    Simulates the queue changes for all EDs and returns the updated queue data
    including load percentage and queue length.
    """
    eds = ED.objects.all()
    ed_data = []

    for ed in eds:
        # Simulate changes in the queue
        if random.choice([True, False]):  # 50% chance to add a new entry
            ed.queue.append(generate_random_triage())
        if ed.queue and random.choice([True, False]):  # 50% chance to remove an entry
            ed.queue.pop(0)
        ed.save()

        # Calculate load percentage
        capacity = 100  # Assuming maximum capacity of 100 users
        load_percentage = min(len(ed.queue) / capacity * 100, 100)

        ed_data.append({
            "name": ed.name,
            "queue_length": len(ed.queue),
            "load": int(load_percentage),
        })

    return JsonResponse({"eds": ed_data})

@login_required
def proceed_to_ed(request, ed_id):
    """
    Handles the user's decision to proceed with the selected ED and places them at the correct position in the queue.
    """
    try:
        ed = ED.objects.get(ed_id=ed_id)
    except ED.DoesNotExist:
        logger.error(f"ED with id {ed_id} does not exist.")
        return render(request, 'errors/404.html', status=404)

    # Get the user's Patient object
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        logger.error(f"Patient object not found for user: {request.user.username}")
        return render(request, 'errors/500.html', {"message": "Patient data is missing. Please complete your profile."})

    # Generate triage data for this patient if not already in session
    triage_data = request.session.get('triage_data')
    if not triage_data:
        triage_data = generate_random_triage()
        request.session['triage_data'] = triage_data

    # Get user position from session
    user_position = request.session.get('user_position')
    if user_position is None:
        # Fallback: Determine user position dynamically
        user_position = max(0, len(ed.queue) - 1)  # Default to end of queue if position is not set
        logger.warning(f"User position not found in session. Defaulting to position {user_position}.")

    # Ensure the user is inserted at the correct position in the queue
    if triage_data not in ed.queue:
        ed.queue.insert(user_position, triage_data)
        ed.save()
        logger.info(f"Inserted user {request.user.username} at position {user_position} in ED {ed.name}'s queue.")

    return render(request, 'selection/proceed_confirmation.html', {
        "ed": ed,
        "user_position": user_position,
        "queue_length": len(ed.queue),
    })



@login_required
def update_position(request, ed_id):
    """
    Updates the user's position in the queue for the given ED.
    """
    try:
        ed = ED.objects.get(ed_id=ed_id)
    except ED.DoesNotExist:
        logger.error(f"ED with id {ed_id} not found.")
        return JsonResponse({"error": "ED not found"}, status=404)

    # Retrieve triage data from the session
    triage_data = request.session.get('triage_data')
    if not triage_data:
        logger.error("Triage data not found in session.")
        return JsonResponse({"error": "Triage data not found"}, status=400)

    # Simulate queue movement: remove only the first item
    if ed.queue and ed.queue[0] != triage_data:  # Avoid removing the user's data prematurely
        removed = ed.queue.pop(0)
        ed.save()
        logger.info(f"ED {ed.name}: Removed from queue: {removed}")

    # Update the user's position if still in the queue
    user_position = None
    if triage_data in ed.queue:
        user_position = ed.queue.index(triage_data)
        request.session['user_position'] = user_position  # Update in session
    else:
        # If not in queue, user is at the front
        user_position = 0
        request.session['user_position'] = user_position

    logger.info(f"ED {ed.name}: User position updated to {user_position}")
    return JsonResponse({"user_position": user_position})

@login_required
def final_confirmation(request, ed_id):
    """
    Displays the final confirmation page after the user has been processed in the queue
    and sends an email notification to the specified address.
    """
    try:
        ed = ED.objects.get(ed_id=ed_id)
    except ED.DoesNotExist:
        return render(request, 'errors/404.html', status=404)

    # Email content
    subject = "User Proceeded to ED Queue"
    message = (
        f"A user has completed the queue for {ed.name}.\n\n"
        "Details:\n"
        f"Name: {request.user.get_full_name()}\n"
        f"Email: {request.user.email}\n"
        f"ED Name: {ed.name}\n"
        f"ED Address: {ed.address}\n"
        "Action: The user is ready to proceed to the ED."
    )
    recipient_list = ['gregory.karachevtsev@gmail.com']  # Your email address

    # Send the email
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        print("Email sent successfully.")  # Debug statement
    except Exception as e:
        print(f"Error sending email: {e}")  # Debug statement

    # Render the confirmation page
    message = f"You are now ready to proceed to {ed.name}. Please follow the instructions provided."
    return render(request, 'selection/final_confirmation.html', {
        "message": message,
    })


@login_required
def admin_dashboard(request):
    """
    Custom Admin dashboard for real-time ED monitoring and user management.
    """
    try:
        admin = request.user.admin
    except AttributeError:
        return render(request, 'errors/403.html', status=403)  # Access denied for non-admins

    eds = ED.objects.all()
    users = User.objects.exclude(is_staff=True)  # Exclude admin/staff accounts from regular users
    doctors = Doctor.objects.all()
    staff = MedicalStaff.objects.all()

    context = {
        "admin": admin,
        "eds": eds,
        "users": users,
        "doctors": doctors,
        "staff": staff,
    }
    return render(request, 'custom-admin/dashboard.html', context)

# Add a JSON endpoint for real-time queue updates
@login_required
def ed_queue_data(request):
    """
    Provide real-time ED queue and load data.
    """
    eds = ED.objects.all()
    ed_data = []
    for ed in eds:
        ed_data.append({
            "name": ed.name,
            "queue_length": len(ed.queue),
            "load_percentage": min(len(ed.queue) / 100 * 100, 100),  # Assuming capacity of 100
        })
    return JsonResponse({"eds": ed_data})



@login_required
def medical_staff_dashboard(request):
    """
    Dashboard for Medical Staff to view all registered users.
    """
    try:
        staff = request.user.medicalstaff
    except AttributeError:
        return render(request, 'errors/403.html', status=403)  # Access denied for non-medical staff

    # Fetch all regular users (exclude staff/admin accounts)
    users = User.objects.exclude(is_staff=True)

    context = {
        "staff": staff,
        "users": users,
    }
    return render(request, 'staff/dashboard.html', context)



@login_required
def admin_realtime_data(request):
    """
    Provide real-time data for the admin dashboard, including ED queues, users, doctors, and staff.
    """
    # Fetch all EDs and their current queue/load data
    eds = ED.objects.all()
    ed_data = []
    for ed in eds:
        if random.choice([True, False]):  # 50% chance to add a new entry
            ed.queue.append(generate_random_triage())
        if ed.queue and random.choice([True, False]):  # 50% chance to remove an entry
            ed.queue.pop(0)
        ed.save()

        # Calculate load percentage
        capacity = 100  # Assuming maximum capacity of 100 users
        load_percentage = min(len(ed.queue) / capacity * 100, 100)
        
        ed_data.append({
            "name": ed.name,
            "queue_length": len(ed.queue),
            "load_percentage": len(ed.queue) / 100 * 100,  # Assuming capacity of 100 for demonstration
        })

    # Fetch all users
    users = list(User.objects.exclude(is_staff=True).values('username', 'first_name', 'last_name', 'email'))

    # Fetch all doctors
    doctors = list(Doctor.objects.all().values('name', 'specialty'))

    # Fetch all medical staff
    staff = list(MedicalStaff.objects.all().values('name', 'role', 'specializing', 'contact_info'))

    return JsonResponse({
        "eds": ed_data,
        "users": users,
        "doctors": doctors,
        "staff": staff,
    })
