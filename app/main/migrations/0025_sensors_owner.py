# Generated by Django 3.2.17 on 2023-10-25 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0024_remove_sensors_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensors',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='測定点'),
        ),
    ]
