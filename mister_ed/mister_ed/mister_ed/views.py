from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("TESTING HOME PAGE")
