# Generated by Django 3.2.17 on 2023-10-25 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_alter_sensors_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensors',
            name='owner',
        ),
    ]
