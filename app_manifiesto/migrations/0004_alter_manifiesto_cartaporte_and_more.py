# Generated by Django 5.0.1 on 2024-10-22 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cartaporte', '0002_initial'),
        ('app_docs', '0006_alter_vehiculo_remolque'),
        ('app_manifiesto', '0003_alter_manifiestoform_txt29'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifiesto',
            name='cartaporte',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manifiestos', to='app_cartaporte.cartaporte'),
        ),
        migrations.AlterField(
            model_name='manifiesto',
            name='conductor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manifiestos', to='app_docs.conductor'),
        ),
        migrations.AlterField(
            model_name='manifiesto',
            name='vehiculo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manifiestos', to='app_docs.vehiculo'),
        ),
    ]