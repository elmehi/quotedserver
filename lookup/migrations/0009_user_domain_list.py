# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 00:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0008_auto_20160419_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='domain_list',
            field=models.TextField(default=''),
        ),
    ]
