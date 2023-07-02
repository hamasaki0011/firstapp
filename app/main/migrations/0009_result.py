# Generated by Django 3.2.17 on 2023-02-27 23:57

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_sensors_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measured_date', models.DateTimeField(default=datetime.datetime(2001, 1, 1, 0, 0), verbose_name='測定日時')),
                ('measured_value', models.FloatField(blank=True, default=0.0, null=True, verbose_name='測定値')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='登録日')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.sensors', verbose_name='センサー')),
            ],
            options={
                'db_table': 'result',
                'unique_together': {('point', 'measured_date')},
            },
        ),
    ]
