# Generated by Django 3.2.17 on 2023-11-08 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_result_value_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='value_unit',
            field=models.CharField(blank=True, default='℃', max_length=4, null=True, verbose_name='単位'),
        ),
    ]