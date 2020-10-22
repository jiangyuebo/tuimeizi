from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('add_favorite/', views.add_favorite, name='add_favorite'),
    path('delete_favorite/<str:media_id_str>', views.delete_favorite, name='delete_favorite'),
]
