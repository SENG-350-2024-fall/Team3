from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Patient
from .factories import PatientFactory

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    date_of_birth = forms.DateField(required=True)
    phone_number = forms.CharField(max_length=10, required=True)
    address = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user_data = {
            'username': self.cleaned_data["username"],
            'first_name': self.cleaned_data["first_name"],
            'last_name': self.cleaned_data["last_name"],
            'email': self.cleaned_data["email"],
            'password': self.cleaned_data["password1"],
            'date_of_birth': self.cleaned_data["date_of_birth"],
            'phone_number': self.cleaned_data["phone_number"],
            'address': self.cleaned_data["address"]
        }
        factory = PatientFactory()
        user = factory.create_user(**user_data)
        return user