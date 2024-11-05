from abc import ABC, abstractmethod
from django.contrib.auth.models import User
from .models import Patient

class UserFactory(ABC):
    @abstractmethod
    def create_user(self, **kwargs):
        pass

class PatientFactory(UserFactory):
    def create_user(self, **kwargs):
        user = User.objects.create_user(
            username=kwargs['username'],
            first_name=kwargs['first_name'],
            last_name=kwargs['last_name'],
            email=kwargs['email'],
            password=kwargs['password']
        )
        Patient.objects.create(
            user=user,
            first_name=kwargs['first_name'],
            last_name=kwargs['last_name'],
            date_of_birth=kwargs['date_of_birth'],
            phone_number=kwargs['phone_number'],
            address=kwargs['address']
        )
        return user