# Generated by Django 5.1.4 on 2025-03-24 14:56

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchhistory',
            name='videos',
        ),
    ]