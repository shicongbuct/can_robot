# Generated by Django 2.1 on 2018-08-15 08:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot_app', '0003_auto_20180815_0801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 15, 8, 2, 56, 206364), verbose_name='添加时间'),
        ),
    ]
