# Generated by Django 3.2.17 on 2023-10-12 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_sensors_site'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sensors',
            unique_together=set(),
        ),
    ]