from django.contrib import admin
from .models import MedicalStaff

# Register your models here
@admin.register(MedicalStaff)
class MedicalStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'specializing', 'contact_info')
