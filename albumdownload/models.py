from django.db import models

import django.utils.timezone as timezone


# Create your models here.
class AlbumTag(models.Model):
    name = models.CharField('标签名', max_length=20)

    class Meta:
        verbose_name = '专辑标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'id: ' + str(self.id) + ' name: ' + self.name


class Album(models.Model):
    title = models.CharField('标题', max_length=200)
    type = models.IntegerField('专辑类型', choices=((1, '图片'), (2, '视频')))
    create_date = models.DateTimeField('创建日期', default=timezone.now)
    tag = models.ForeignKey(AlbumTag, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = '专辑'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'id: ' + str(self.id) + ' title: ' + self.title


class AlbumPic(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    is_cover = models.BooleanField('是否封面', default=False)
    remote_url = models.CharField('远程地址', max_length=200, null=True, blank=True)
    local_url = models.CharField('本地地址', max_length=200, null=True, blank=True)
    pic = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = '专辑图片'
        verbose_name_plural = verbose_name


class AlbumDownloadPath(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    download_path = models.CharField('下载地址', max_length=200, null=True, blank=True)
    code = models.CharField('提取码', max_length=20, null=True, blank=True)
    password = models.CharField('解压密码', max_length=20, null=True, blank=True)
    create_date = models.DateTimeField('创建时间', default=timezone.now)

    class Meta:
        verbose_name = '专辑下载地址'
        verbose_name_plural = verbose_name
