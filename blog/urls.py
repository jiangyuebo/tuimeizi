from django.urls import path
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from blogproject.settings import common

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('poster/<str:user_id_str>', views.detail, name='detail'),
    path('enjoy/<str:media_id_str>', views.enjoy, name='enjoy'),
    path('search/', views.search, name='search'),
    path('favorite/', views.favorite, name='favorite'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(common.MEDIA_URL, document_root=common.MEDIA_ROOT)
