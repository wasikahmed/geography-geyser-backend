from .base import *

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.setdefault('SECRET_KEY', 'django-insecure-l5tdl19q+t8imusp66ho52ndscqs(qf683@1#y9kgmc#%w((t%')

# Strict allowed hosts from ENV
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}