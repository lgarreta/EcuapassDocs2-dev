# Generated by Django 5.0.1 on 2024-09-02 22:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_cartaporte', '0002_initial'),
        ('app_docs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartaporte',
            name='destinatario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cartaportes_destinatario', to='app_docs.cliente'),
        ),
        migrations.AlterField(
            model_name='cartaporte',
            name='documento',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='app_cartaporte.cartaportedoc'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cartaporte',
            name='remitente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cartaportes_remitente', to='app_docs.cliente'),
        ),
    ]