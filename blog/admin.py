from django.contrib import admin
from .models import Post, Category, Tag, Media, Poster, DeletedMedia

from .utils import tweets_operator, system_tools

from PIL import Image, ImageChops
import dhash


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
    # 增加自定义按钮
    actions = ['delete_duplicate_images_from_poster']

    # 重写poster保存方法
    def save_model(self, request, obj, form, change):
        tweets_operator.setup_poster_and_fetch_tweets(obj.user_screen_name, obj.category)
        self.message_user(request, '添加成功')

    def delete_duplicate_images_from_poster(self, request, queryset):
        for poster in queryset:
            # 获取poster id
            poster_id_str = poster.user_id_str
            # 遍历该poster所有media
            poster_media = Media.objects.filter(user_id_str=poster_id_str)
            hash_image_dic = {}
            for media in poster_media:
                # 媒体文件类型
                media_type = media.media_type
                if not media_type == "video":
                    # 媒体文件地址
                    local_url = media.local_url
                    # 计算图片 d hash 值
                    d_hash_of_image = d_hash_of_the_image(local_url)
                    d_hash_str = str(d_hash_of_image)
                    # 判断当前字典中是否已存在这个hash的对象
                    if d_hash_str in hash_image_dic.keys():
                        # 已存在该 d hash的图片
                        # 判断当前图片是否封面
                        if media.is_cover:
                            # 是封面，删除另外一张
                            target_media = hash_image_dic[d_hash_str]
                            target_media_local_url = target_media.local_url
                            # 记录删除媒体
                            deleted_media_record = DeletedMedia(post_id_str=target_media.post_id_str,
                                                                media_id_str=target_media.media_id_str)
                            deleted_media_record.save()
                            # 删除文件
                            tweets_operator.delete_local_file_by_path(target_media_local_url)
                            # 删除数据
                            target_media.delete()

                            # 并将当前这张放入字典
                            hash_image_dic[d_hash_str] = media
                            print("删除一张")
                        else:
                            # 不是封面，删除当前这张
                            # 记录删除媒体
                            deleted_media_record = DeletedMedia(post_id_str=media.post_id_str,
                                                                media_id_str=media.media_id_str)
                            deleted_media_record.save()

                            media_local_url = media.local_url
                            # 删除文件
                            tweets_operator.delete_local_file_by_path(media_local_url)
                            # 删除信息
                            media.delete()
                            print("删除一张")
                    else:
                        # 不存在该 d hash的图片,存入
                        hash_image_dic[d_hash_str] = media

        self.message_user(request, '清除完成')

    delete_duplicate_images_from_poster.short_description = "专辑图片去重"


# 对比两张图片是否一样
def compare_images(path_one, path_two):
    image_one = Image.open(path_one)
    image_two = Image.open(path_two)

    try:
        diff = ImageChops.difference(image_one, image_two)
        if diff.getbbox() is None:
            # 图片完全一样
            return True
        else:
            return False
    except ValueError:
        pass


# 计算图片的 d hash
def d_hash_of_the_image(image_path):
    the_image = Image.open(image_path)
    try:
        row, col = dhash.dhash_row_col(the_image)
        the_d_hash = dhash.format_hex(row, col)
        return the_d_hash
    except OSError:
        pass


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
admin.AdminSite.site_header = 'TuiMeiZi'
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
