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
from django.contrib.auth import login as auth_login
from .forms import RegisterForm

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
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {"form": form})
