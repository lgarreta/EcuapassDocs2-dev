# Generated by Django 5.0.1 on 2024-10-04 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_docs', '0005_vehiculo_sexo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehiculo',
            name='sexo',
        ),
        migrations.AddField(
            model_name='conductor',
            name='sexo',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]