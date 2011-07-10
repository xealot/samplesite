import site, os
from settings_local import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            'ec2-50-16-237-98.compute-1.amazonaws.com:11211',
            'ec2-50-16-187-208.compute-1.amazonaws.com:11211',
        ]
    }
}