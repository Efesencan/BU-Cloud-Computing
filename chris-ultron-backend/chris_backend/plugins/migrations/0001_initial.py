# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-02 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(default='ds', max_length=4)),
            ],
            options={
                'ordering': ('type',),
            },
        ),
    ]
