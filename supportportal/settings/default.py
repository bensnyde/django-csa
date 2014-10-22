from database import *
from private import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

AUTH_USER_MODEL = 'contacts.contact'

ALLOWED_HOSTS = []

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = '/home/mostrecent/supportportal/uploads/'
MEDIA_URL = '/media/'

STATIC_ROOT = '/home/mostrecent/supportportal/static/'
STATIC_URL = '/assets/'
STATICFILES_DIRS = (
    "/home/mostrecent/supportportal/templates/assets",
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    '/home/mostrecent/supportportal/templates',
)

INSTALLED_APPS = (
    'apps.contacts',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.zenoss',
    'apps.servers',
    'apps.services',
    'apps.companies',
    'apps.opensrs',
    'apps.dns',
    'apps.solusvm',   
    'apps.vmware',   
    'apps.email',
    'apps.ftp', 
    'apps.ip',
    'apps.dashboard',
    'apps.support.tickets',
    'apps.support.knowledgebase',
    'apps.support.contact',
    'apps.search',
    'apps.loggers',
    'apps.backend',
    'apps.announcements',
    'apps.reports',
    'apps.affiliates',
    'common',
    'libs'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'formatter': 'verbose'
        },
        'request_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': 'logs/django_request.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
        },        
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },        
    }
}
