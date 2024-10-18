from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
class CustomLoginView(LoginView):
    template_name = 'login.html'
    
def home(request):
    return HttpResponse("TEMP HOME PAGE")

def triage(request):
    return HttpResponse("TEMP TRIAGE PAGE")

def login(request):
    return HttpResponse("TEMP LOGIN PAGE")

def signup(request):
    return HttpResponse("TEMP SIGNUP PAGE")