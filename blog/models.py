from django.db import models
from django.urls import reverse
from django.utils import timezone

from blogproject.settings import common

# Create your models here.

# 分类
from django.utils.html import format_html


class Category(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'id: ' + str(self.id) + ' name: ' + self.name


# 标签
class Tag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 文章 （用以记录每次需要删除的媒体文件，方便后续一键删除）
class Post(models.Model):
    # 文章标题
    title = models.CharField('标题', max_length=70)
    # 正文
    body = models.CharField('正文', max_length=144, blank=True)
    # 创建时间
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    # 修改时间
    modified_time = models.DateTimeField('修改时间')
    # 文章摘要
    excerpt = models.CharField('摘要', max_length=140, blank=True)
    # 发表人
    poster = models.CharField('发表人', max_length=30, blank=True)

    # 关联表
    # 分类，一对多（一篇文章只能一个分类，一个分类可以多篇文章）
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    # 标签，多对多（一篇文章可有多个标签，一个标签可有多篇文章）
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    # 汉化
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    # 复写save方法，保证每次操作都会重新设置修改时间
    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()
        super().save(*args, **kwargs)

    # 自定义 get_absolute_url 方法
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})


# Media 媒体资源
class Media(models.Model):
    # user id
    user_id_str = models.CharField('发推用户id', max_length=36)
    # post id
    post_id_str = models.CharField('推文id', max_length=36)
    # post text
    post_text = models.CharField('推文文字', max_length=144, blank=True)
    # media id
    media_id_str = models.CharField('媒体资源ID', max_length=36)
    # media type
    media_type = models.CharField('媒体类型', max_length=10)
    # remote url
    remote_url = models.CharField('远程地址', max_length=200)
    # local url
    local_url = models.CharField('本地路径', max_length=100)
    # local video url
    local_video_url = models.CharField('本地视频路径', max_length=100, blank=True)
    # created time
    created_at = models.DateField()
    # cover flag
    is_cover = models.BooleanField('是否封面', blank=True)
    # insert time stamp
    insert_timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    # 后台管理界面展示字段 - 图片预览
    def preview(self):
        return format_html('<img src="{}" width="400px"/>', self.get_media_display_path(), )

    # 后台管理界面展示字段 - 查看链接
    def enjoy_link(self):
        return format_html('<a href="{}" >enjoy</a>', self.get_absolute_url(), )

    class Meta:
        verbose_name = '媒体'
        verbose_name_plural = verbose_name
        ordering = ['-insert_timestamp']

    def __str__(self):
        media_data = 'user_id:' + self.user_id_str + \
                     ',post_id_str:' + \
                     self.post_id_str + \
                     ',post_text:' + \
                     self.post_text + \
                     ',media_type:' + \
                     self.media_type + \
                     ',remote_url:' + \
                     self.remote_url + \
                     ',local_url:' + \
                     self.local_url + \
                     ',created_at:' + \
                     str(self.created_at) + \
                     ',is_cover:' + \
                     str(self.is_cover)
        return media_data

    def get_media_display_path(self):
        # 判断是否包含mnt
        if "mnt" in self.local_url:
            # 是扩展存储
            path_list = self.local_url.split('/media/')
            path = '/media/' + path_list[1]
        else:
            path_list = self.local_url.split('/media/')
            path = '/media/' + path_list[1]
        return path

    def get_video_display_path(self):
        # 判断是否包含mnt
        if "mnt" in self.local_url:
            path_list = self.local_video_url.split('/media/')
            path = '/media/' + path_list[1]
        else:
            path_list = self.local_video_url.split('/media/')
            path = '/media/' + path_list[1]
        return path

    def get_absolute_url(self):
        return reverse('blog:enjoy', kwargs={'media_id_str': self.media_id_str})

    def get_pre_media_absolute_url(self):
        # 获取所有此poster的media
        poster_medias = Media.objects.filter(user_id_str=self.user_id_str).order_by("id")
        # 获取上一个media的ID
        pre_media = poster_medias.filter(id__gt=self.id).first()
        if pre_media is not None:
            final_media_id_str = pre_media.media_id_str
        else:
            final_media_id_str = self.media_id_str
        return reverse('blog:enjoy', kwargs={'media_id_str': final_media_id_str})

    def get_next_media_absolute_url(self):
        # 获取所有此poster的media
        poster_medias = Media.objects.filter(user_id_str=self.user_id_str).order_by("id")
        # 获取下一个media的ID
        next_media = poster_medias.filter(id__lt=self.id).all().order_by("-id").first()
        if next_media is not None:
            final_media_id_str = next_media.media_id_str
        else:
            final_media_id_str = self.media_id_str
        return reverse('blog:enjoy', kwargs={'media_id_str': final_media_id_str})


class Poster(models.Model):
    # user id
    user_id_str = models.CharField('用户ID', max_length=18, blank=True)
    # user screen name
    user_screen_name = models.CharField('用户名英文', max_length=30)
    # user name
    user_name = models.CharField('用户名中文', max_length=30, blank=True)
    # create time
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    # poster category
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    # views count
    poster_views = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return 'screen_name:' + self.user_screen_name + ", user_id:" + self.user_id_str + " ,user_name:" + self.user_name

    # 自定义 get_absolute_url 方法
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={
            'user_id_str': self.user_id_str
        })

    # 模型方法，阅读量 +1
    def increase_views(self):
        self.poster_views += 1
        self.save(update_fields=['poster_views'])


# 已删除媒体记录
class DeletedMedia(models.Model):
    post_id_str = models.CharField('推文id', max_length=36)
    media_id_str = models.CharField('媒体资源ID', max_length=36)


# 媒体D Hash值记录
class MediaDHashRecord(models.Model):
    d_hash = models.CharField('媒体文件D Hash值', max_length=300, blank=True, null=True)
