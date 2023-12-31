# Generated by Django 3.2.17 on 2023-09-28 13:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_profile_tel_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='phone_number',
        ),
        migrations.AlterField(
            model_name='profile',
            name='tel_number',
            field=models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message="電話番号は、'09012345678'のようにハイフンを省略して入力してください！", regex='^[0-9]+$')], verbose_name='緊急連絡先'),
        ),
    ]
