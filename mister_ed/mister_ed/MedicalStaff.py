from django.contrib.auth.models import User
from mister_ed.models import MedicalStaff
import uuid

# Create a user
user = User.objects.create_user(
    username="drsmithy",
    password="password123",
    first_name="John",
    last_name="Smith",
    email="drsmith@example.com"
)

# Create a MedicalStaff instance linked to the user
staff = MedicalStaff.objects.create(
    user=user,  # Link to the User instance
    staff_id=uuid.uuid4(),
    name=f"{user.first_name} {user.last_name}",
    role="Doctor",
    specializing="Cardiology",
    contact_info="555-1234"
)
