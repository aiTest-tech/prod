# Generated by Django 5.1.3 on 2024-12-02 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wtc', '0008_alter_wtc_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wtc',
            name='message',
            field=models.TextField(blank=True, max_length=10000, null=True),
        ),
    ]
