from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("home/", views.home, name="home"),
    path("triage/", views.triage, name="triage"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("book_appointment/<uuid:schedule_id>/", views.book_appointment, name="book_appointment"),
]