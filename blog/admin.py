from django.contrib import admin
from .models import Post, Category, Tag, Media, Poster

from .utils import tweets_operator


class PostAdmin(admin.ModelAdmin):
    # 控制post列表展示字段
    list_display = ['title', 'created_time', 'modified_time', 'category', 'author']
    # 控制表单展示字段
    fields = ['title', 'body', 'excerpt', 'category', 'tags']

    # 自动保存作者
    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    fields = ['user_screen_name', 'category']
    # 后台列表展示字段
    list_display = ('user_id_str', 'user_screen_name', 'user_name', 'category', 'poster_views')

    # 重写poster保存方法
    def save_model(self, request, obj, form, change):
        tweets_operator.setup_poster_and_fetch_tweets(obj.user_screen_name, obj.category)
        self.message_user(request, '添加成功')


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    fields = ['media_id_str', 'remote_url', 'is_cover']
    list_display = ('media_id_str', 'remote_url', 'is_cover')
    search_fields = ['user_id_str', 'media_id_str']


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
