# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-26 18:43
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid
import velo.payment.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0003_auto_20170126_1840'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivePaymentChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateTimeField()),
                ('till_date', models.DateTimeField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DailyTransactionTotals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('calculated_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('reported_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(default={})),
            ],
            options={
                'abstract': False,
            },
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
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('usage_times', models.IntegerField(default=1)),
                ('usage_times_left', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment.DiscountCampaign')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_discountcode_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_discountcode_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('company_name', models.CharField(blank=True, max_length=100, verbose_name='Uzņēmuma nosaukums / Vārds Uzvārds')),
                ('company_vat', models.CharField(blank=True, max_length=100, verbose_name='VAT Numurs')),
                ('company_regnr', models.CharField(blank=True, max_length=100, verbose_name='Uzņēmuma numurs / Personas kods')),
                ('company_address', models.CharField(blank=True, max_length=100, verbose_name='Adrese')),
                ('company_juridical_address', models.CharField(blank=True, max_length=100, verbose_name='Juridiskā adrese')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('invoice_show_names', models.BooleanField(default=True, verbose_name='Rādīt dalībnieku vārdus rēķinā')),
                ('slug', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('file', models.FileField(blank=True, upload_to=velo.payment.models.get_invoice_upload, verbose_name='Invoice')),
                ('series', models.CharField(blank=True, max_length=10, verbose_name='Competition series')),
                ('number', models.IntegerField(blank=True, null=True, verbose_name='Series invoice number')),
                ('access_time', models.TimeField(blank=True, null=True)),
                ('access_ip', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('erekins_code', models.CharField(blank=True, max_length=100)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('donation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('status', models.SmallIntegerField(choices=[(10, 'Jauns'), (20, 'Gaida'), (30, 'OK'), (-10, 'Atgriezts'), (-20, 'Atcelts'), (-30, 'Laiks notecējis'), (-40, 'Noraidīts'), (-50, 'Neizdevās'), (-60, 'Kļūda'), (-70, 'ID nav atrodams')], default=10)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.ActivePaymentChannel')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
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
                ('params', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('url', models.CharField(blank=True, max_length=255)),
                ('server_url', models.CharField(blank=True, max_length=255)),
                ('key_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='config/certificates/'), upload_to='', verbose_name='Private Key')),
                ('cert_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='config/certificates/'), upload_to='', verbose_name='Certificate or Public Key')),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('from_year', models.IntegerField(default=0)),
                ('till_year', models.IntegerField(default=2050)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('start_registering', models.DateTimeField(blank=True, null=True)),
                ('end_registering', models.DateTimeField(blank=True, null=True)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Competition')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_price_set', to=settings.AUTH_USER_MODEL)),
                ('distance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Distance')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_price_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('distance', 'start_registering'),
                'permissions': (('can_see_totals', 'Can see income totals'),),
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('code', models.CharField(default=uuid.uuid4, max_length=36, unique=True)),
                ('status', models.SmallIntegerField(choices=[(-70, 'ID nav atrodams'), (-60, 'Kļūda'), (-50, 'Neizdevās'), (-40, 'Noraidīts'), (-30, 'Laiks notecējis'), (-20, 'Atcelts'), (-10, 'Atgriezts'), (10, 'Jauns'), (20, 'Gaida'), (30, 'OK')], default=10)),
                ('external_code', models.CharField(blank=True, max_length=50)),
                ('external_code_requested', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20, verbose_name='Total amount')),
                ('information', models.CharField(blank=True, max_length=255)),
                ('language', models.CharField(default='lv', max_length=10)),
                ('created_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('server_response_at', models.DateTimeField(blank=True, null=True)),
                ('user_response_at', models.DateTimeField(blank=True, null=True)),
                ('server_response', models.TextField(blank=True)),
                ('user_response', models.TextField(blank=True)),
                ('returned_user_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('returned_server_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('should_be_reviewed', models.BooleanField(default=False)),
                ('integration_id', models.CharField(blank=True, max_length=50)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment.PaymentChannel')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_transaction_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_transaction_set', to=settings.AUTH_USER_MODEL)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment.Payment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='invoice',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment.PaymentChannel'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='competition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Competition', verbose_name='Sacensības'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_invoice_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_invoice_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='payment.Payment', verbose_name='Maksājums'),
        ),
        migrations.AddField(
            model_name='dailytransactiontotals',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment.PaymentChannel'),
        ),
        migrations.AddField(
            model_name='dailytransactiontotals',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_dailytransactiontotals_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dailytransactiontotals',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_dailytransactiontotals_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activepaymentchannel',
            name='payment_channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment.PaymentChannel'),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('series', 'number')]),
        ),
    ]
