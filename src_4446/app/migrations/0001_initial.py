# Generated by Django 5.1.3 on 2024-12-02 05:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ASRData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('min', models.IntegerField()),
                ('is_succ', models.BooleanField(default=False)),
                ('api_hit', models.IntegerField(default=0)),
                ('data', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asr_data', to='base.data')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
