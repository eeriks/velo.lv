# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_album_is_agency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='folder',
            field=models.FilePathField(allow_files=False, allow_folders=True, path='media/gallery/', recursive=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='kind',
            field=models.PositiveSmallIntegerField(choices=[(1, 'YouTube'), (2, 'Vimeo')], default=1),
        ),
        migrations.AlterField(
            model_name='video',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0),
        ),
    ]
