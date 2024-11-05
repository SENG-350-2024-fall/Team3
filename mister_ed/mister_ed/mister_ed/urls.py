from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("home/", views.home, name="home"),
    path("triage/", views.triage, name="triage"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path('resources/', views.resources, name='resources'),
    path('resources/healthy-living/', views.healthy_living, name='healthy_living'),
    path('resources/mental-health/', views.mental_health, name='mental_health'),
    path('resources/nutrition/', views.nutrition, name='nutrition'),
    path('resources/exercise-essentials/', views.exercise_essentials, name='exercise_essentials'),
    path('resources/stress-management/', views.stress_management, name='stress_management'),
    path('resources/eating-on-budget/', views.eating_on_budget, name='eating_on_budget'),
    path('resources/resource-of-the-day/', views.resource_of_the_day, name='resource_of_the_day'),

]