from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("triage/", views.triage, name="triage"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", views.signup, name="signup"),
]