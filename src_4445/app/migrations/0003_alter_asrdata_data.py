# Generated by Django 5.1.3 on 2024-11-25 12:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_initial'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asrdata',
            name='data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asr_data', to='base.data'),
        ),
    ]
