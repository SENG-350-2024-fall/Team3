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
from .forms import ProfileForm
from .models import Profile


@login_required(login_url="/login") 
def home(request):
    return render(request, 'home/home.html')

def triage(request):
    return HttpResponse("TEMP TRIAGE PAGE")

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

@login_required(login_url="/login") 
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if created:
        profile.user = request.user
        profile.save()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, initial={'photo': profile.photo})
    return render(request, 'profile/profile.html', {'form': form})

