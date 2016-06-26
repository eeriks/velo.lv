# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-26 00:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivePaymentChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateTimeField()),
                ('till_date', models.DateTimeField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCampaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('discount_entry_fee_percent', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discount_entry_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discount_insurance_percent', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('discount_insurance', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('usage_times', models.IntegerField(default=1)),
                ('usage_times_left', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.DiscountCampaign')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_discountcode_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_discountcode_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('legacy_id', models.IntegerField(blank=True, null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('erekins_code', models.CharField(blank=True, max_length=100)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('donation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('status', models.SmallIntegerField(choices=[(10, 'New'), (20, 'Pending'), (30, 'OK'), (-10, 'Reversed'), (-20, 'Cancelled'), (-30, 'Timeout'), (-40, 'Declined'), (-50, 'Failed'), (-60, 'Error'), (-70, 'ID not found')], default=10)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.ActivePaymentChannel')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_payment_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_payment_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_channel', models.CharField(default='LKDF', max_length=20)),
                ('title', models.CharField(max_length=50)),
                ('image_slug', models.CharField(blank=True, max_length=50)),
                ('erekins_url_prefix', models.CharField(blank=True, max_length=50)),
                ('erekins_auth_key', models.CharField(blank=True, max_length=100)),
                ('erekins_link', models.CharField(blank=True, max_length=50)),
                ('is_bill', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('from_year', models.IntegerField(default=0)),
                ('till_year', models.IntegerField(default=2050)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('start_registering', models.DateTimeField(blank=True, null=True)),
                ('end_registering', models.DateTimeField(blank=True, null=True)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_price_set', to=settings.AUTH_USER_MODEL)),
                ('distance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Distance')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_price_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('distance', 'start_registering'),
                'permissions': (('can_see_totals', 'Can see income totals'),),
            },
        ),
        migrations.AddField(
            model_name='activepaymentchannel',
            name='payment_channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.PaymentChannel'),
        ),
    ]
