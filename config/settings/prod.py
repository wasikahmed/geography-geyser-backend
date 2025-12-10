from .base import *

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.setdefault('SECRET_KEY')

# Strict allowed hosts from ENV
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')