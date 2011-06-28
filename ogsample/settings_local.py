import site
site.addsitedir('./ogsample')

from settings_global import *

ROOT_URLCONF = 'ogsample.urls'
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'extra.lib.auth.RemoteAccount',
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DETECT_TZ = True
CREDIT_TYPE = 'sample'

RPC_API_TOKEN = 'QUjoQulIYUkesENezuWevIyOgOJOJOMUPemeGozExUriReZeXU'
RPC_ENDPOINT = 'https://organogold.securehomeoffice.com/api/v3/rpc'

LOGIN_URL = '/login/'

INSTALLED_APPS += (
    'sample',
)

STATICFILES_DIRS += (
    'ogsample/static/',
)

TEMPLATE_DIRS += (
    'ogsample/templates/',
)
