from .base import *

ALLOWED_HOSTS = ['*']

# Add for django tool bar 
INSTALLED_APPS += [
    'debug_toolbar',
]

# Add for django tool bar
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR,'db.sqlite3'),
    # }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'sensor_data',
    #     'USER': 'fujico',
    #     'PASSWORD': 'admin.fujico',
    #     'HOST': 'localhost',
    #     'PORT': '5432'
    # }
    'default': {
        'ENGINE': env('SQL_ENGINE'),
        'NAME': env('SQL_DATABASE'),
        'USER': env('SQL_USER'),
        'PASSWORD': env('SQL_PASSWORD'),
        'HOST': env('SQL_HOST'),
        'PORT': env('SQL_PORT')
    }    
}
# the contents of .env.dev
# SQL_ENGINE=django.db.backends.postgresql
## SQL_ENGINE2=django.db.backends.postgresql_psycopg2
# SQL_DATABASE=sensor_data
# SQL_USER=fujico
# SQL_PASSWORD=admin.fujico
# SQL_HOST=localhost
# SQL_PORT=5432
# DATABASE=postgres

# Add for django tool bar
INTERNAL_IPS = ['127.0.0.1']

# Add for django tool bar
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Add for django tool bar
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
}