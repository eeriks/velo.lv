# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-18 15:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20160408_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='legacy_id',
        ),
        migrations.RemoveField(
            model_name='news',
            name='tmp_string',
        ),
    ]