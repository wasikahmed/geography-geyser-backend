from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.setdefault('SECRET_KEY', 'django-insecure-l5tdl19q+t8imusp66ho52ndscqs(qf683@1#y9kgmc#%w((t%')

# default to allow everything if ALLOWED_HOSTS is missing in .env
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'