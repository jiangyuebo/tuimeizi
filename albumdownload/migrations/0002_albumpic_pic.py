# Generated by Django 3.1.1 on 2020-10-30 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albumdownload', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='albumpic',
            name='pic',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
