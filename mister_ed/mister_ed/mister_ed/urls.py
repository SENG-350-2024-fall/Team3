from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("home/", views.home, name="home"),
    path("triage/", views.triage, name="triage"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
]