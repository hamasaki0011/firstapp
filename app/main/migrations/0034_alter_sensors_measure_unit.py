# Generated by Django 3.2.17 on 2023-11-09 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_sensors_measure_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensors',
            name='measure_unit',
            field=models.CharField(blank=True, default='℃', max_length=4, null=True, verbose_name='測定単位'),
        ),
    ]
