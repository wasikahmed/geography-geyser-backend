import sys
import os
import environ
from pathlib import Path

env = environ.Env() # initialize environ
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))

# go up 3 levels: settings -> config -> root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# add apps directory to the path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Application definition
INSTALLED_APPS = [
    # django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',

    # local apps
    'users',

    # third party
    'rest_framework',
    'rest_framework_simplejwt',


    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'cloudinary_storage',
    'cloudinary',
]

# Site ID is required by django-allauth
SITE_ID = 1

# Provider Config
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'VERIFIED_EMAIL': True,
    }
}

# Tell dj-rest-auth to use your existing JWT setup
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'my-app-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'my-app-refresh-token',
    # This prevents it from trying to use the standard token model
    'TOKEN_MODEL': None, 
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware', 
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Database
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
        )
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'


# auth user model
AUTH_USER_MODEL = 'users.User'

# DRF Config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ALLAUTH CONFIGURATION
# ------------------------------------------------------------------------------
# Tell allauth that we don't use a username field
ACCOUNT_USER_MODEL_USERNAME_FIELD = None 

# Tell allauth that email is required and unique
# ACCOUNT_EMAIL_REQUIRED = True 


# Tell allauth that username is NOT required
# ACCOUNT_USERNAME_REQUIRED = False 

# Tell allauth to authenticate using email
# ACCOUNT_AUTHENTICATION_METHOD = 'email' 

# Optional: Avoids sending a verification email immediately on social login 
# (since Google/Social emails are usually already verified)
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# NEW SETTINGS (Add these)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'none'

# 1. Replace ACCOUNT_AUTHENTICATION_METHOD with this:
ACCOUNT_LOGIN_METHODS = {'email'}

# 2. Replace ACCOUNT_EMAIL_REQUIRED and ACCOUNT_USERNAME_REQUIRED with this:
# This list defines the fields required during signup. 
# 'email*' means email is required.
ACCOUNT_SIGNUP_FIELDS = ['email*', 'first_name', 'last_name', 'phone_number'] 
# (Note: You can adjust the list above based on what fields you actually want in the signup form)


# Use BigAutoField as the default primary key field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Cloudinary configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Media settings
MEDIA_URL = '/media/'  # Public URL for media