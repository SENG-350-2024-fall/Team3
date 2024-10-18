from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView

    
def home(request):
    return render(request, 'home/home.html')

def triage(request):
    return HttpResponse("TEMP TRIAGE PAGE")

def login(request):
    return render(request, 'login/login.html')

def signup(request):
    return HttpResponse("TEMP SIGNUP PAGE")