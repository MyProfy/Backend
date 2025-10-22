import os
import urllib
from datetime import timedelta
from pathlib import Path

from .env import (
    SECRET_KEY,
    DEBUG,
    ALLOWED_HOSTS,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = SECRET_KEY
DEBUG = DEBUG
ALLOWED_HOSTS = ALLOWED_HOSTS

INSTALLED_APPS = [
    'unfold',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'phonenumber_field',
    'corsheaders',
    'payme',
    'import_export',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'api.auth.PhoneBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'api.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

APPEND_SLASH = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
CSRF_TRUSTED_ORIGINS = [
    'https://myprofy.uz',
    'https://www.myprofy.uz'
]
CORS_ALLOWED_ORIGINS = [
    'https://myprofy.uz',
    'https://www.myprofy.uz',
    "http://localhost:3001",
    "http://localhost:3000",
    "http://139.59.247.170:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Set-Cookie', 'Content-Type', 'X-CSRFToken']

# Cookie settings
# SESSION_COOKIE_NAME = 'sessionid'
# CSRF_COOKIE_NAME = 'csrftoken'
# SESSION_COOKIE_AGE = 86400
# SESSION_COOKIE_DOMAIN = 'myprofy.uz'
# CSRF_COOKIE_DOMAIN = 'myprofy.uz'
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SAMESITE = 'None'

# Payme settings
PAYME_ID = "685d093f15461d903a41b09f"
PAYME_KEY = "Za0Dx2cPp%%ZDnvbAPexFeyBacxx@G5OO2rD"
PAYME_ACCOUNT_FIELD = "boost_payment_id"
PAYME_AMOUNT_FIELD = "price"
PAYME_ACCOUNT_MODEL = "api.models.BoostPayment"
PAYME_ONE_TIME_PAYMENT = True

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),

}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.api.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

STATICFILES_DIRS = [
    BASE_DIR / 'backend' / 'static',
]

UNFOLD = {
    "THEME": "light",
    "SITE_TITLE": "MyProfy Админ",
    "SITE_HEADER": "MyProfy",
    "SITE_SUBHEADER": "Панель управления",
    "LOGO": {
        "url": "/static/images/logo.png",
        "alt": "MyProfy",
    },
    "COLORS": {
    "base": {
        "50": "#ffffff",
        "100": "#f8f9fa",
        "200": "#f1f3f4",
        "300": "#dee2e6",
        "400": "#ced4da",
        "500": "#adb5bd",
        "600": "#6c757d",
        "700": "#495057",
        "800": "#343a40",
        "900": "#000000",
    },
    "primary": {
        "500": "#3da03f",
        "600": "#2e7d32",
        "700": "#15803d",
    },
    "font": {
        "default-light": "#000000",
        "important-light": "#000000",
        "subtle-light": "#333333",
        "default-dark": "#f1f1f1",
        "important-dark": "#ffffff",
        "subtle-dark": "#dddddd",
        },
    },
    "STYLES": [
    lambda request: "data:text/css;charset=utf-8," + urllib.parse.quote("""
        input:not([type="checkbox"]),
        textarea,
        select {
            color: black !important;
            background-color: white !important;
        }
        input[type="checkbox"] {
            accent-color: #3da03f !important; /* зелёный в стиле твоей темы */
            width: 18px;
            height: 18px;
        }
    """),
    ],
}


INSTALLED_APPS += [
    "unfold.contrib.filters",
    "unfold.contrib.forms",
]

BOT_NAME = "myprofy_bot"

if DEBUG:
    SESSION_COOKIE_DOMAIN = None
    CSRF_COOKIE_DOMAIN = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
