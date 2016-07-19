# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 06:12
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.translation import activate


def run_sqls(apps, schema_editor):
    CompetitionSupporter = apps.get_model("supporter", "CompetitionSupporter")

    supporters = CompetitionSupporter.objects.order_by('competition_id', '-support_level', 'ordering')
    last_competition_id = None
    ordering = 0
    for supporter in supporters:
        if last_competition_id != supporter.competition_id:
            last_competition_id = supporter.competition_id
            ordering = 0
        else:
            ordering += 1

        supporter.ordering = ordering
        activate('en')
        supporter.support_title_en = supporter.get_support_level_display()

        if supporter.support_level == 90:
            supporter.support_title_lv = "Ģenerālsponsors"
            supporter.support_title_ru = "Генеральный спонсор"
            supporter.is_large_logo = True
        elif supporter.support_level == 80:
            supporter.support_title_lv = "Oficiālie partneri"
            supporter.support_title_ru = "Официальные партнеры"
        elif supporter.support_level == 70:
            supporter.support_title_lv = "Sponsors"
            supporter.support_title_ru = "Спонсор"
        elif supporter.support_level == 65:
            supporter.support_title_lv = "Oficiālais balvu sponsors"
            supporter.support_title_ru = "Официальный спонсор призов"
        elif supporter.support_level == 40:
            supporter.support_title_lv = "Oficiālais tehniskais partneris"
            supporter.support_title_ru = "Официальный технический партнер"
        elif supporter.support_level == 35:
            supporter.support_title_lv = "Oficiālais enerģijas dzēriens"
            supporter.support_title_ru = "Официальный энергетический напиток"
        elif supporter.support_level == 34:
            supporter.support_title_lv = "Oficiālais ūdens"
            supporter.support_title_ru = "Официальная вода"
        elif supporter.support_level == 30:
            supporter.support_title_lv = "Partneri"
            supporter.support_title_ru = "Партнеры"
        elif supporter.support_level == 10:
            supporter.support_title_lv = "Atbalstītājs"
            supporter.support_title_ru = "Болельщик"

        supporter.save()

class Migration(migrations.Migration):

    dependencies = [
        ('supporter', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='supporter',
            options={'ordering': ('title',)},
        ),
        migrations.RemoveField(
            model_name='competitionsupporter',
            name='label',
        ),
        migrations.RemoveField(
            model_name='supporter',
            name='description',
        ),
        migrations.RemoveField(
            model_name='supporter',
            name='ordering',
        ),
        migrations.RemoveField(
            model_name='supporter',
            name='supporter_kind',
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='is_large_logo',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='support_title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='support_title_en',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='support_title_lv',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='support_title_ru',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='competitionsupporter',
            name='ordering',
            field=models.IntegerField(default=1000),
        ),
        migrations.RunPython(run_sqls),
    ]
