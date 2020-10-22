from django.contrib import admin

from .models import UserInformation, Favorite


# Register your models here.
@admin.register(UserInformation)
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'nick_name', 'gender', 'information_user', 'score', 'level_score')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('favorite_user', 'favorite_media_id', 'create_date')
