# Generated by Django 5.1.2 on 2024-11-05 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mister_ed', '0003_alter_profile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo',
            field=models.ImageField(default='profile_photos/default.jpg', upload_to='profile_photos/'),
        ),
    ]
