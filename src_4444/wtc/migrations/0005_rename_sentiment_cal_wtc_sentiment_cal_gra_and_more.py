# Generated by Django 5.1.3 on 2024-11-26 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wtc', '0004_wtc_depr_rout_wtc_lo_sc_wtc_sentiment_cal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wtc',
            old_name='sentiment_cal',
            new_name='sentiment_cal_gra',
        ),
        migrations.AddField(
            model_name='wtc',
            name='sentiment_cal_pol',
            field=models.TextField(blank=True, null=True),
        ),
    ]
