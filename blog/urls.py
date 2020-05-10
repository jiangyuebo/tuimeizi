from django.urls import path
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from blogproject import settings

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('poster/<str:user_id_str>/', views.detail, name='detail'),
    path('enjoy/<str:media_id_str>', views.enjoy, name='enjoy'),
    path('archives/<int:year>/<int:month>/', views.archive, name='archive'),
    path('categories/<int:pk>', views.category, name='category'),
    path('tags/<int:pk>/', views.tag, name='tag'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)