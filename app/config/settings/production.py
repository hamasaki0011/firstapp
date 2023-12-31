from .base import *

# if based on auth/.env 
ALLOWED_HOSTS =  os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
# if based on .env.dev
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {    
            
    'default': {
        # 'ENGINE': env('DB_ENGINE'),
        # 'NAME': env('DB_NAME'),
        # 'USER': env('DB_USER'),
        # 'PASSWORD': env('DB_PASSWORD'),
        # 'PORT': env('DB_PORT')
        'ENGINE': env('SQL_ENGINE'),
        'NAME': env('SQL_DATABASE'),
        'USER': env('SQL_USER'),
        'PASSWORD': env('SQL_PASSWORD'),
        'HOST': env('SQL_HOST'),
        'PORT': env('SQL_PORT')
    }
}

# The static and media files path on the deploy
# These are from docker-compose.prod.yml
STATIC_ROOT = '/home/app/web/staticfiles'
MEDIA_ROOT = '/home/app/web/mediafiles'

# The below codes were generated from django-debug-toolbar settings
# STATIC_ROOT = '/usr/share/nginx/html/static'
# MEDIA_ROOT = '/usr/share/nginx/html/media'