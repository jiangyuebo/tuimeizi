from django.contrib import admin
from .models import Post, Category, Tag, Media, Poster, DeletedMedia

from .utils import tweets_operator, system_tools


class PostAdmin(admin.ModelAdmin):
    # 控制post列表展示字段
    list_display = ['title', 'created_time', 'modified_time', 'category']
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
    # 修改的时候允许修改的字段
    fields = ['media_id_str', 'local_url', 'remote_url', 'is_cover']
    # 表格显示的字段
    list_display = ('media_id_str', 'preview', 'media_type', 'created_at', 'enjoy_link', 'is_cover', 'insert_timestamp')
    # 添加搜索框
    search_fields = ['user_id_str', 'media_id_str']
    # 增加自定义按钮
    actions = ['delete_selected_media_data_and_file', 'delete_no_owner_media_file']
    # 根据创建时间排序
    ordering = ('-insert_timestamp',)
    # 顶部和底部都显示操作栏
    actions_on_top = True
    actions_on_bottom = True
    # 显示选中项数目
    actions_selection_counter = True
    # 每页记录限制
    list_per_page = 50

    def delete_selected_media_data_and_file(self, request, queryset):
        for media in queryset:
            # 记录删除媒体
            deleted_media_record = DeletedMedia(post_id_str=media.post_id_str, media_id_str=media.media_id_str)
            deleted_media_record.save()
            # 先删除数据库相关数据
            media.delete()
            # 获取文件本地存储路径
            local_path = media.local_url
            # 删除本地文件
            tweets_operator.delete_local_file_by_path(local_path)
        self.message_user(request, '删除成功')

    delete_selected_media_data_and_file.short_description = '删除数据及本地文件'

    def delete_no_owner_media_file(self, request, queryset):
        clear_result = system_tools.folder_clear()
        clear_kb = float(clear_result['recover_byte']) / 1024
        clear_mb = clear_kb / 1024
        clear_space = format(clear_mb, '.2f')
        clear_errors = clear_result['errors']
        if clear_errors:
            result_str = clear_errors
        else:
            result_str = "清理完成： 扫描文件：" + str(clear_result['scan_count']) + "个，删除文件：" + str(clear_result['delete_count']) + "个，获得空间：" + str(clear_space) + "mb"
        self.message_user(request, result_str)

    delete_no_owner_media_file.short_description = '删除磁盘中无主媒体文件'


@admin.register(DeletedMedia)
class DeletedMediaAdmin(admin.ModelAdmin):
    # 修改的时候允许修改的字段
    fields = ['post_id_str', 'media_id_str']
    # 表格显示的字段
    list_display = ('post_id_str', 'media_id_str')


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
