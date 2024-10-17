from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("TEMP HOME PAGE")

def triage(request):
    return HttpResponse("TEMP TRIAGE PAGE")

def login(request):
    return HttpResponse("TEMP LOGIN PAGE")

def signup(request):
    return HttpResponse("TEMP SIGNUP PAGE")