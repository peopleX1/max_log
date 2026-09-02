from pathlib import Path
import os

#from django.utils.translation import gettext_lazy as _

from apps.core.utils import load_env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#load_env(BASE_DIR / "config/.env.prod")
load_env(BASE_DIR / "config/.env")

SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG'))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')


# Application definition

INSTALLED_APPS = [
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # project apps
    'apps.core',
    'apps.users',
    # 3rd party libraries
    'phonenumber_field',
    'django_cleanup',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesStandaloneBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            Path(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# #ASGI
# ASGI_APPLICATION = 'config.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('POSTGRES_ENGINE'),
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# User
AUTH_USER_MODEL = 'users.CustomUser'

# Login\logout
LOGIN_REDIRECT_URL = 'homepage'
# LOGOUT_REDIRECT_URL = 'users:login'
# LOGIN_URL = 'users:login'
#REQUIRE_LOGIN_PUBLIC_NAMED_URLS = (LOGIN_URL, LOGOUT_REDIRECT_URL, )
REQUIRE_LOGIN_PUBLIC_URLS = ('/hidden-admin/',)

TIME_INPUT_FORMATS = ['%H:%M']

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'

STATIC_ROOT = Path(BASE_DIR, 'static')

STATICFILES_DIRS = [
    Path(BASE_DIR, 'staticfiles'),
]

MEDIA_URL = '/media/'

MEDIA_ROOT = Path(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGES = [
    ('en', 'English'),
]

# django axes
AXES_ENABLED = True
AXES_RESET_ON_SUCCESS = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 5
AXES_LOCKOUT_PARAMETERS = ["username",]
AXES_LOCKOUT_TEMPLATE = Path(BASE_DIR, 'templates/lockout.html')

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880 #5mb

# Set additinal settings
if bool(os.environ.get('DEVELOP')):
    from config.settings_dev import *
else:
    from config.settings_prod import *
