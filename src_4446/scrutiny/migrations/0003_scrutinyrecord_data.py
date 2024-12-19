# Generated by Django 5.1.3 on 2024-12-02 06:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('scrutiny', '0002_remove_scrutinyrecord_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrutinyrecord',
            name='data',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='scrutiny_data', to='base.data'),
            preserve_default=False,
        ),
    ]
