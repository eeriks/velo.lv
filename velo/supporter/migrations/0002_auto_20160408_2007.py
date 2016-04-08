# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 20:07
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields
import velo.supporter.models


class Migration(migrations.Migration):

    dependencies = [
        ('supporter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logo',
            name='image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, height_field='height', upload_to=velo.supporter.models._get_logo_upload_path, width_field='width'),
        ),
    ]
