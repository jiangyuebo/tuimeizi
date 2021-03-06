# Generated by Django 3.0.5 on 2020-05-06 01:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20200505_1729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poster',
            name='poster_category',
        ),
        migrations.AlterField(
            model_name='poster',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 6, 1, 19, 52, 378323, tzinfo=utc), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='poster',
            name='user_id_str',
            field=models.CharField(blank=True, max_length=18, verbose_name='用户ID'),
        ),
        migrations.AlterField(
            model_name='poster',
            name='user_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='用户名中文'),
        ),
    ]
