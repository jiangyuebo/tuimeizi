from django.contrib import admin
from .models import Album, AlbumTag, AlbumPic, AlbumDownloadPath


# Register your models here.
class AlbumPicInline(admin.StackedInline):
    model = AlbumPic
    extra = 4


class AlbumDownloadPathInline(admin.StackedInline):
    model = AlbumDownloadPath
    exec = 1


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    fields = ['title', 'type', 'tag', 'create_date']

    # 后台列表展示字段
    list_display = ('title', 'type', 'tag', 'create_date')
    inlines = [AlbumPicInline, AlbumDownloadPathInline]


@admin.register(AlbumTag)
class AlbumTagAdmin(admin.ModelAdmin):
    fields = ['name']

    # 后台列表展示字段
    list_display = ("name",)


@admin.register(AlbumPic)
class AlbumPicAdmin(admin.ModelAdmin):
    fields = ['album', 'is_cover', 'remote_url', 'local_url']

    # 后台列表展示字段
    list_display = ('album', 'remote_url', 'local_url', 'is_cover')


@admin.register(AlbumDownloadPath)
class AlbumDownloadPathAdmin(admin.ModelAdmin):
    fields = ['album', 'download_path', 'password', 'create_date']

    # 后台列表展示字段
    list_display = ('album', 'download_path', 'password', 'create_date')
