# Generated by Django 5.0.1 on 2024-10-04 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_docs', '0006_remove_vehiculo_sexo_conductor_sexo'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='certificado',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
