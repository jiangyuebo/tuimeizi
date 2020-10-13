# Generated by Django 2.2.3 on 2020-10-12 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_delete_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False, verbose_name='激活状态')),
                ('nick_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='昵称')),
                ('birthday', models.DateTimeField(blank=True, null=True, verbose_name='生日')),
                ('gender', models.CharField(choices=[('girl', '女'), ('boy', '男')], max_length=10, verbose_name='性别')),
            ],
            options={
                'verbose_name': '用户额外信息',
                'verbose_name_plural': '用户额外信息',
            },
        ),
    ]
