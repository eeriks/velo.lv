# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-12 08:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20160408_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.ActivePaymentChannel'),
        ),
    ]