# Generated by Django 3.0.5 on 2020-05-02 01:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20200502_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='poster_views',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='poster',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 2, 1, 51, 58, 119765, tzinfo=utc), verbose_name='创建时间'),
        ),
    ]
