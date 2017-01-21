# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-13 18:39
from __future__ import unicode_literals

from django.utils import timezone
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0003_auto_20170106_2012'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyTransactionTotals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('date', models.DateTimeField(default=timezone.now)),
                ('calculated_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('reported_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.PaymentChannel')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_dailytransactiontotals_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_dailytransactiontotals_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
