from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.viptuimeizi.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'blog.apps.BlogConfig',
]

CRONJOBS = [
    ('* */2 * * *', 'blog.utils.tweets_operator.fetch_tweets_data_from_target_posters')
]
