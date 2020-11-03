from django.urls import path

from . import views

app_name = 'album'
urlpatterns = [
    path('album', views.album_index, name='album'),
    path('album_detail/<str:album_id>', views.album_detail, name='album_detail'),
]
