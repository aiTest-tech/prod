# Generated by Django 5.1.3 on 2024-12-02 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(help_text='Name of the API (e.g., ASR, Sentiment, Scrutiny)', max_length=50)),
                ('total_minutes_called', models.FloatField(default=0, help_text='Total minutes called for this API')),
                ('total_requests', models.IntegerField(default=0, help_text='Total requests made to this API')),
                ('successful_requests', models.IntegerField(default=0, help_text='Total successful requests')),
                ('failed_requests', models.IntegerField(default=0, help_text='Total failed requests')),
            ],
        ),
    ]
