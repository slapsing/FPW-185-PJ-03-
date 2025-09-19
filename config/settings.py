import os
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

#####
# env
#####

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", '').split(',')

SITE_ID = os.getenv("SITE_ID")
SITE_URL = os.getenv("SITE_URL")

#####
# base
#####

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

#####
# packages
#####

INSTALLED_APPS += [
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
    # "modeltranslation",


    "drf_spectacular",

    "crispy_forms",
    "crispy_bootstrap5",
    'django.contrib.humanize',
    "ckeditor",
    "ckeditor_uploader",

]

#####
# Apps
#####

INSTALLED_APPS += [
    'board.apps.BoardConfig',
    'sign',
    'appointment',

]

#####
# MIDDLEWARE
#####

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

#####
# TEMPLATES
#####

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'board.context_processors.unread_notifications_count',
            ],
        },
    },
]
#####
# CRISPY
#####

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

#####
# Internationalization + i18n
#####

LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
]

USE_I18N = True
USE_L10N = True
USE_TZ = True

#####
# modeltranslation
#####

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en')

#####
# static
#####

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#####
# Media
#####

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

#####
# django-ckeditor
#####

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_IMAGE_BACKEND = "pillow"


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Embed', 'Youtube'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['Undo', 'Redo'],
        ],
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',
            'embed',
            'autoembed',
            'youtube',
            'widget',
            'lineutils',
            'clipboard',
        ]),
        'removePlugins': 'stylesheetparser',
    },
}


#####
# Email backend
#####

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ("true", "1", "yes")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
ADMINS = os.getenv("ADMINS")
SERVER_EMAIL = os.getenv("SERVER_EMAIL")

#####
# django-allauth
#####

ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'email', 'username'}

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_REDIRECT_URL = "/auth/profile/"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/account/login/"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/profile/"

ACCOUNT_EMAIL_SUBJECT_PREFIX = "[MMORPG Fanboard] "

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/auth/profile/"
LOGOUT_REDIRECT_URL = "/"

EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

#####
# REST framework + drf-spectacular
#####

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "MMORPG Fanboard API",
    "DESCRIPTION": "API для доски объявлений игрового сообщества",
    "VERSION": "1.0.0",
}


#####
# celery+redis
#####

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

CELERY_BEAT_SCHEDULE = {
    'send-newsletter-every-monday-9am': {
        'task': 'appointment.tasks.send_weekly_newsletter',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
}

