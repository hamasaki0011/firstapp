from .base import *

# 2023.7.14 Need to set env file later 
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
ALLOWED_HOSTS =  os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR,'db.sqlite3'),
    # }
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'PORT': env('DB_PORT')
    }
}

# STATIC_ROOT = '/usr/share/nginx/html/static'
# MEDIA_ROOT = '/usr/share/nginx/html/media'