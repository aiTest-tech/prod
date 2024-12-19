# Generated by Django 5.1.3 on 2024-12-18 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_alter_asrdata_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="CaptchaMedia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
                ("captcha", models.ImageField(upload_to="media/")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]