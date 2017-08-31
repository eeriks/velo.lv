# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-26 21:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_auto_20170407_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='ucicategory',
            name='group',
            field=models.CharField(blank=True, max_length=60),
        ),
        migrations.AlterField(
            model_name='application',
            name='payment_status',
            field=models.SmallIntegerField(choices=[(0, 'Nav apmaksāts'), (10, 'Gaida maksājumu'), (20, 'Apmaksāts'), (30, "Won't pay"), (-10, 'Atcelts')], default=0, verbose_name='Maksājuma statuss'),
        ),
    ]