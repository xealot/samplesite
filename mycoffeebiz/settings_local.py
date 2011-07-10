import site, os
from settings_global import *

site.addsitedir(os.path.abspath('./mycoffeebiz')) #This is so we can reference applications and views at the MCB level.
ROOT_PATH = os.path.abspath(os.path.dirname(__file__)) #For referencing templates and files.

ROOT_URLCONF = 'urls'
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'extra.lib.auth.RemoteAccount',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ]
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

LOGIN_URL = '/login/'

INSTALLED_APPS += (
    'main',
)

STATICFILES_DIRS += (
    ROOT_PATH + '/static/',
)

TEMPLATE_DIRS += (
    ROOT_PATH + '/templates/',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.static',
    'extra.middleware.customdata.context',
)

MIDDLEWARE_CLASSES += (
    'extra.middleware.customdata.CustomDataMiddleware',
    'extra.middleware.sslredirect.SSLRedirectMiddleware',
)

CUSTOMDATA_WEBSITE_SLUG = 'mycoffeebiz'
CUSTOMDATA_USER_SLUG_PATTERN = 'hostname'
CUSOTMDATA_REDIRECT_ON_MISS = 'no-site'
CUSTOMDATA_HOSTNAMES = ('*.ubuntu.local:8888',)

RPC_API_TOKEN = 'QUjoQulIYUkesENezuWevIyOgOJOJOMUPemeGozExUriReZeXU'
RPC_ENDPOINT = 'https://mycoffeebiz.securehomeoffice.com/api/v3/rpc/'

SSL_ENABLED = True
SSL_USE_HTTPS = False
SSL_FAKE = False
SSL_FULL_COVERAGE = True
SSL_DOMAIN = 'admin.secure.ubuntu.local:8888'
SSL_SEND_SESSION = True
