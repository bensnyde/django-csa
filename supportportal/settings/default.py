from database import *
from private import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

LOGIN_REDIRECT_URL = '/dashboard/index/'
LOGIN_URL = '/login/'

AUTH_USER_MODEL = 'contacts.Contact'

ALLOWED_HOSTS = []

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = './uploads/'
MEDIA_URL = '/media/'

STATIC_ROOT = './static/'
STATIC_URL = '/assets/'
STATICFILES_DIRS = (
    "./templates/assets",
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
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
    './templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'appsdir.contacts.apps.ContactsConfig',
    'appsdir.companies.apps.CompaniesConfig',
    'appsdir.announcements.apps.AnnouncementsConfig',
    'appsdir.knowledgebase.apps.KnowledgebaseConfig',
    'appsdir.support.apps.SupportConfig',
    'appsdir.loggers.apps.LoggersConfig',
    'appsdir.groups.apps.GroupsConfig',
    'appsdir.dashboard',
    'appsdir.reports',
    'appsdir.search',
    'common',
    'rest_framework',
    'rest_framework.authtoken',
    'simple_history',
    'actstream',
    'watson',
)

REST_FRAMEWORK = {
    'PAGINATE_BY': 10,                 # Default to 10
    'PAGINATE_BY_PARAM': 'limit',      # Allow client to override, using `?limit=xxx`.
    'MAX_PAGINATE_BY': 100             # Maximum limit allowed when using `?limit=xxx`.
}

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
