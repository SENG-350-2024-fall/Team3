from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm

@login_required(login_url="/login") 
def home(request):
    return render(request, 'home/home.html')

@login_required(login_url="/login") 
def triage(request):
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
        }]
    return render(request, 'home/resources.html', {'resources': resources})

def login(request):
    return render(request, 'registration/login.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('/home')
    elif request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/home')  # Redirect to the home page after successful registration
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
