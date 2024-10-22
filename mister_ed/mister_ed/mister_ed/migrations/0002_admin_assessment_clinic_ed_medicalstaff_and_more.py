# Generated by Django 4.2.9 on 2024-10-18 05:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mister_ed", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Admin",
            fields=[
                (
                    "admin_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(max_length=255)),
                ("phone_number", models.TextField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Assessment",
            fields=[
                (
                    "assessment_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("recommended_action", models.TextField()),
                ("assessment_date", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Clinic",
            fields=[
                (
                    "clinic_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255)),
                ("phone_number", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="ED",
            fields=[
                (
                    "ed_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("address", models.CharField(default="", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="MedicalStaff",
            fields=[
                (
                    "staff_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("role", models.CharField(max_length=255)),
                ("specializing", models.CharField(max_length=255)),
                ("contact_info", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="SeverityLevel",
            fields=[
                (
                    "severity_level_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("description", models.TextField()),
                ("priority", models.IntegerField()),
            ],
        ),
        migrations.RemoveField(model_name="patient", name="id",),
        migrations.AddField(
            model_name="patient",
            name="address",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="patient",
            name="patient_id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="patient",
            name="first_name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="patient",
            name="last_name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="patient",
            name="phone_number",
            field=models.CharField(
                max_length=10,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be exactly 10 digits.",
                        regex="^\\d{10}$",
                    )
                ],
            ),
        ),
        migrations.CreateModel(
            name="TriageCriteria",
            fields=[
                (
                    "triage_criteria_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("description", models.TextField()),
                (
                    "admin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mister_ed.admin",
                    ),
                ),
                (
                    "severity_level",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mister_ed.severitylevel",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "schedule_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date", models.DateField()),
                ("shift", models.CharField(max_length=255)),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mister_ed.medicalstaff",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PatientData",
            fields=[
                (
                    "patient_data_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("medical_history", models.TextField()),
                ("current_symptoms", models.TextField()),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mister_ed.assessment",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "notification_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("message", models.TextField()),
                ("date_time", models.DateTimeField()),
                (
                    "recipient_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EDCapacity",
            fields=[
                (
                    "ed_capacity_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("current_capacity", models.IntegerField(default=0)),
                ("max_capacity", models.IntegerField(default=0)),
                ("wait_time_estimate", models.TimeField(blank=True)),
                (
                    "ed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mister_ed.ed"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="assessment",
            name="severity_level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="mister_ed.severitylevel",
            ),
        ),
        migrations.AddField(
            model_name="assessment",
            name="staff",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="mister_ed.medicalstaff"
            ),
        ),
        migrations.AddField(
            model_name="assessment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "appointment_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date_time", models.DateTimeField()),
                (
                    "clinic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mister_ed.clinic",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
