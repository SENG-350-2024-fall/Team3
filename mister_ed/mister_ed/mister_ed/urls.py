from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("triage/", views.triage, name="triage"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
]