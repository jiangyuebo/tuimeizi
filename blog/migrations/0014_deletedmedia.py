# Generated by Django 3.1.1 on 2020-11-05 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_remove_post_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id_str', models.CharField(max_length=36, verbose_name='推文id')),
                ('media_id_str', models.CharField(max_length=36, verbose_name='媒体资源ID')),
            ],
        ),
    ]
