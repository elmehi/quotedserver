# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 02:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0005_auto_20160418_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.date(2016, 4, 18)),
        ),
        migrations.AlterField(
            model_name='source',
            name='source_date',
            field=models.DateTimeField(default=datetime.date(2016, 4, 18)),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_created',
            field=models.DateTimeField(default=datetime.date(2016, 4, 18)),
        ),
    ]
