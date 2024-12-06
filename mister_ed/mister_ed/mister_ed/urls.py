from django.contrib import admin
from django.urls import include, path

from . import views
from .views import CustomLoginView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
    path("home/", views.home, name="home"),
    path("triage/", views.triage, name="triage"),
    path("signup/", views.signup, name="signup"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("book_appointment/<uuid:schedule_id>/", views.book_appointment, name="book_appointment"),
    path('resources/', views.resources, name='resources'),
    path('resources/healthy-living/', views.healthy_living, name='healthy_living'),
    path('resources/mental-health/', views.mental_health, name='mental_health'),
    path('resources/nutrition/', views.nutrition, name='nutrition'),
    path('resources/exercise-essentials/', views.exercise_essentials, name='exercise_essentials'),
    path('resources/stress-management/', views.stress_management, name='stress_management'),
    path('resources/eating-on-budget/', views.eating_on_budget, name='eating_on_budget'),
    path('resources/resource-of-the-day/', views.resource_of_the_day, name='resource_of_the_day'),
    path("medical_records/", views.medical_records, name="medical_records"),
    path('virtual_meetings/', views.virtual_meetings, name='virtual_meetings'),
    path('ed_locations/', views.ed_locations, name='ed_locations'),
    path('profile/', views.profile, name='profile'),
    path('update_ed_loads/', views.update_ed_loads, name='update_ed_loads'),
    path('ed_detail/<uuid:ed_id>/', views.ed_detail, name='ed_detail'),
    path('proceed/<uuid:ed_id>/', views.proceed_to_ed, name='proceed'),
    path('update_position/<uuid:ed_id>/', views.update_position, name='update_position'),
    path('final_confirmation/<uuid:ed_id>/', views.final_confirmation, name='final_confirmation'),
    path("custom-admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("staff/dashboard/", views.medical_staff_dashboard, name="medical_staff_dashboard"),
    path("custom-admin/ed_queue_data/", views.ed_queue_data, name="ed_queue_data"),
    path("custom-admin/realtime-data/", views.admin_realtime_data, name="admin_realtime_data"),

]   
