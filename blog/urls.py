from django.urls import path
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from blogproject import settings

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('poster/<str:user_id_str>/<str:user_name>', views.detail, name='detail'),
    path('enjoy/<str:media_id_str>', views.enjoy, name='enjoy'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)