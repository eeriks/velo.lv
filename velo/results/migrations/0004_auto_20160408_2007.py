# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_auto_20150926_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leader',
            name='color',
            field=models.CharField(choices=[('blue', 'blue'), ('red', 'red'), ('green', 'green'), ('sea', 'sea'), ('orange', 'orange'), ('yellow', 'yellow')], max_length=50),
        ),
        migrations.AlterField(
            model_name='result',
            name='status',
            field=models.CharField(blank=True, choices=[('DSQ', 'DSQ'), ('DNS', 'DNS'), ('DNF', 'DNF')], max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points1',
            field=models.IntegerField(blank=True, null=True, verbose_name='1.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points2',
            field=models.IntegerField(blank=True, null=True, verbose_name='2.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points3',
            field=models.IntegerField(blank=True, null=True, verbose_name='3.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points4',
            field=models.IntegerField(blank=True, null=True, verbose_name='4.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points5',
            field=models.IntegerField(blank=True, null=True, verbose_name='5.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points6',
            field=models.IntegerField(blank=True, null=True, verbose_name='6.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='distance_points7',
            field=models.IntegerField(blank=True, null=True, verbose_name='7.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points1',
            field=models.IntegerField(blank=True, null=True, verbose_name='1.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points2',
            field=models.IntegerField(blank=True, null=True, verbose_name='2.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points3',
            field=models.IntegerField(blank=True, null=True, verbose_name='3.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points4',
            field=models.IntegerField(blank=True, null=True, verbose_name='4.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points5',
            field=models.IntegerField(blank=True, null=True, verbose_name='5.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points6',
            field=models.IntegerField(blank=True, null=True, verbose_name='6.'),
        ),
        migrations.AlterField(
            model_name='sebstandings',
            name='group_points7',
            field=models.IntegerField(blank=True, null=True, verbose_name='7.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points1',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='1.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points2',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='2.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points3',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='3.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points4',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='4.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points5',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='5.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points6',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='6.'),
        ),
        migrations.AlterField(
            model_name='teamresultstandings',
            name='points7',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='7.'),
        ),
        migrations.AlterField(
            model_name='urlsync',
            name='kind',
            field=models.CharField(default='FINISH', max_length=30),
        ),
    ]