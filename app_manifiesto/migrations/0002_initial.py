# Generated by Django 5.0.1 on 2024-10-21 19:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_docs', '0001_initial'),
        ('app_manifiesto', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='manifiesto',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='manifiesto',
            name='vehiculo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vehiculo', to='app_docs.vehiculo'),
        ),
        migrations.AddField(
            model_name='manifiesto',
            name='documento',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='app_manifiesto.manifiestoform'),
        ),
    ]
