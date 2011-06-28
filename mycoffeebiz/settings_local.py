import site, os
from settings_global import *

site.addsitedir('./mycoffeebiz') #This is so we can reference applications and views at the MCB level.
ROOT_PATH = os.path.abspath(os.path.dirname(__file__)) #For referencing templates and files.

ROOT_URLCONF = 'urls'
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'extra.lib.auth.RemoteAccount',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

RPC_API_TOKEN = 'QUjoQulIYUkesENezuWevIyOgOJOJOMUPemeGozExUriReZeXU'
RPC_ENDPOINT = 'https://organogold.securehomeoffice.com/api/v3/rpc/'

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
)