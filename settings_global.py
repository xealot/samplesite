import site, os
site.addsitedir(os.path.abspath('./thirdparty'))

ROOT_PATH = os.path.abspath(os.path.dirname(__file__)) #For referencing templates and files.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

DETECT_TZ = False

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'sample',
        'USER':     'sample_user',
        'PASSWORD': 'wer3sdfwer3sdf',
        'HOST':     'ngplatformdb.cwbzqfhg63he.us-east-1.rds.amazonaws.com',
        'PORT':     '3306',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

SECRET_KEY = '8$1lk2xg5+6&#q+sxw64juvubm!gi4by%_s1$+p8zcykrddn!t'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django_jinja2.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    'extra.lib.context_processors.step_processor',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'extra.middleware.urlsession.URLSessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'extra.middleware.security.AccessCheckMiddleware',
    'extra.middleware.timezone.TimezoneMiddleware',
    'extra.middleware.abort.AbortMiddleware',
)

TEMPLATE_DIRS = (
    ROOT_PATH + '/templates/',
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'sample',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(levelname)s [%(name)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'basic'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.db': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'] if DEBUG else ['null'],
        'level': 'DEBUG',
    }
}