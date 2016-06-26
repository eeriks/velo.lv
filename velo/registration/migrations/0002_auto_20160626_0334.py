# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-26 00:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('team', '0001_initial'),
        ('core', '0001_initial'),
        ('payment', '0001_initial'),
        ('registration', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team.Team'),
        ),
        migrations.AddField(
            model_name='participant',
            name='where_heard',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.Choices', verbose_name='Where Heard'),
        ),
        migrations.AddField(
            model_name='number',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition'),
        ),
        migrations.AddField(
            model_name='number',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_number_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='number',
            name='distance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Distance'),
        ),
        migrations.AddField(
            model_name='number',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_number_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant_set', to='registration.CompanyApplication'),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_companyparticipant_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='distance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Distance'),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_companyparticipant_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='team_member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team.Member'),
        ),
        migrations.AddField(
            model_name='companyapplication',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition'),
        ),
        migrations.AddField(
            model_name='companyapplication',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_companyapplication_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companyapplication',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_companyapplication_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='application',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition', verbose_name='Competition'),
        ),
        migrations.AddField(
            model_name='application',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_application_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='application',
            name='discount_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.DiscountCode'),
        ),
        migrations.AddField(
            model_name='application',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_application_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='number',
            unique_together=set([('competition', 'number', 'group')]),
        ),
    ]
