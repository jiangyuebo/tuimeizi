from django.db import models
from django.contrib.auth.models import User

import django.utils.timezone as timezone


# Create your models here.
class UserInformation(models.Model):
    is_active = models.BooleanField(verbose_name="激活状态", default=False)
    nick_name = models.CharField(verbose_name="昵称", max_length=20, null=True, blank=True)
    birthday = models.DateTimeField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(choices=(('girl', '女'), ('boy', '男')), max_length=10, verbose_name="性别")
    information_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "用户额外信息"
        verbose_name_plural = verbose_name


class EmailVerifyCode(models.Model):
    code = models.CharField(max_length=20, verbose_name="邮箱验证码")
    email = models.EmailField(max_length=200, verbose_name="验证码邮箱")
    send_type = models.IntegerField(choices=((1, 'register'), (2, 'forget'), (3, 'change')), verbose_name="验证码类型")
    create_date = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name
