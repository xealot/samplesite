import site
site.addsitedir('./thirdparty')

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'extra.middleware.security.AccessCheckMiddleware',
    'extra.middleware.timezone.TimezoneMiddleware',
    'extra.middleware.abort.AbortMiddleware',
)

TEMPLATE_DIRS = (
    'templates/',
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
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}