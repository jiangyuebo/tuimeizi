# Generated by Django 3.0.5 on 2020-04-30 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20200427_0731'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='local_video_url',
            field=models.CharField(blank=True, max_length=100, verbose_name='本地视频路径'),
        ),
        migrations.AlterField(
            model_name='media',
            name='is_cover',
            field=models.BooleanField(blank=True, verbose_name='是否封面'),
        ),
    ]
