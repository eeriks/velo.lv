# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-27 11:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20161227_1135'),
        ('registration', '0003_participant_ssn_hashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.Invoice'),
        ),
    ]
