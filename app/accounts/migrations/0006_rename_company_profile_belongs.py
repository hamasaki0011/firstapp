# Generated by Django 3.2.17 on 2023-03-28 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_profile_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='company',
            new_name='belongs',
        ),
    ]
