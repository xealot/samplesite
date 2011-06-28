import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../thirdparty')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'ogsample.settings_local'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()