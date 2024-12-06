from django.contrib.auth.models import User
from mister_ed.models import Admin
import uuid

# Create a user for the admin
user = User.objects.create_user(
    username="adminuser123",
    password="adminpassword123",
    first_name="Admin",
    last_name="User",
    email="admin@example.com"
)

# Grant admin privileges
user.is_staff = True  # Allows access to the Django admin site
user.is_superuser = True  # Optional: Grants all permissions
user.save()

# Create an Admin instance associated with the user
admin = Admin.objects.create(
    admin_id=uuid.uuid4(),
    name=f"{user.first_name} {user.last_name}",
    phone_number="555-5678",
    user=user  # This links the Admin to the User instance
)

print(f"Admin {admin.name} created successfully with username '{user.username}' and admin privileges!")
