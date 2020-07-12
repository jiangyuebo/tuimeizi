from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u=h7m^^ow&r@t_6r7uwh2=*p9cd$2$9ku04ih7gt8kq156^$yw'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog.apps.BlogConfig',
]
