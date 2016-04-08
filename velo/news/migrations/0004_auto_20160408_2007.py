# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20150819_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0),
        ),
        migrations.AlterField(
            model_name='news',
            name='language',
            field=models.CharField(choices=[('lv', 'Latviski'), ('en', 'English')], db_index=True, default='lv', max_length=20, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='news',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='news',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0),
        ),
        migrations.AlterField(
            model_name='news',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0),
        ),
    ]
