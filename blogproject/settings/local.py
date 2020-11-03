from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mh97fl=2_!6n(e7)obj%ix5n%_95d+%-xxamdi$slwvpd$uule'
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

    # our apps
    'blog.apps.BlogConfig',
    'accounts.apps.AccountsConfig',
    'analytics.apps.AnalyticsConfig',
    'mypayment.apps.MypaymentConfig',
    'albumdownload.apps.AlbumdownloadConfig',
    'captcha'
]
