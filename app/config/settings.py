"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
#import environ
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# Setting the environ
#env = environ.Env()
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = int(os.environ.get("DEBUG", default=0))

# ALLOWED_HOSTS = ['localhost']
# ALLOWED_HOSTS = ['hamasaki.pythonanywhere.com']
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Application definitiongit 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',  # Forgetting this was probably your error
    'main.apps.MainConfig',
    'record.apps.RecordConfig',
    "accounts",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        # 'DIRS': [],
        # 'DIRS': [BASE_DIR / 'templates'], 
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


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR,'db.sqlite3'),
    #}
        "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

AUTH_USER_MODEL = 'accounts.User'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS=[BASE_DIR / 'static_local']
# STATIC_ROOT=os.path.join(BASE_DIR,'static')
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / "media_local"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Set-up the allauth
AUTHENTICATION_BACKENDS = [ 
  'django.contrib.auth.backends.ModelBackend',     
  'allauth.account.auth_backends.AuthenticationBackend',
] 

SITE_ID = 1

#ユーザーネームは使わない
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
#認証にはメールアドレスを使用する 
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
#ログイン後のリダイレクト先を指定
from django.urls import reverse_lazy
LOGIN_REDIRECT_URL = reverse_lazy('main:main_index')
#ログアウト後のリダイレクト先を指定
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("account_login")
#メールアドレスが確認済みである必要がある
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
#即ログアウトとする
ACCOUNT_LOGOUT_ON_GET = True
# Emailをターミナルに表示する
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ACCOUNT_ADAPTER = "accounts.adapter.ProfileAdapter"

# CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Default logging for Django. This sends an email to the site admins on every
# HTTP 500 error. Depending on DEBUG, all other log records are either sent to
# the console (DEBUG=True) or discarded (DEBUG=False) by means of the
# require_debug_true filter.
# LOGGING = {
#      'version': 1,
#      'disable_existing_loggers': False,
#      'filters': {
#          'require_debug_false': {
#              '()': 'django.utils.log.RequireDebugFalse',
#          },
#          'require_debug_true': {
#              '()': 'django.utils.log.RequireDebugTrue',
#          },
#      },
#      'formatters': {
#          'django.server': {
#              '()': 'django.utils.log.ServerFormatter',
#              'format': '[%(server_time)s] %(message)s a',
#          }
#      },
#      'handlers': {
#          'console': {
#              'level': 'INFO',
#              'filters': ['require_debug_true'],
#              'class': 'logging.StreamHandler',
#          },
#          'django.server': {
#              'level': 'INFO',
#              'class': 'logging.StreamHandler',
#              'formatter': 'django.server',
#          },
#          'mail_admins': {
#              'level': 'ERROR',
#              'filters': ['require_debug_false'],
#              'class': 'django.utils.log.AdminEmailHandler'
#          }
#      },
#      'loggers': {
#          'django': {
#              'handlers': ['console', 'mail_admins'],
#              'level': 'INFO',
#          },
#          'django.server': {
#              'handlers': ['django.server'],
#              'level': 'INFO',
#              'propagate': False,
#          },
        
# #         #追加
#         'main': {
#             'handlers': ['console'],
#             'level': 'INFO',
#             'propagate': False,
#         },
#      }
#}

#if not DEBUG:
#    #ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
#    STATIC_ROOT = 'usr/share/nginx/html/static'
#    MEDIA_ROOT = 'usr/share/nginx/html/media'
    

