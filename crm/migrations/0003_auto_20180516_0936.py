# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-16 01:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0002_auto_20180426_1529'),
        ('crm', '0002_auto_20180515_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='password',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='username',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='auth',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.UserInfo'),
        ),
    ]
