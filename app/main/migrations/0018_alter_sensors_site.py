# Generated by Django 3.2.17 on 2023-10-24 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_alter_sensors_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensors',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.location', verbose_name='現場'),
        ),
    ]