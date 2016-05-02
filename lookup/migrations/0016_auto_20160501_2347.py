# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 04:47
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0015_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='other_trusted',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='source',
            name='other_untrusted',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='source',
            name='trusted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='source',
            name='untrusted',
            field=models.BooleanField(default=False),
        ),
    ]
