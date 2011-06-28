import pytz
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from extra.rpc import rpc
from extra.lib.tz import LocalTimezone

TZ_ATTR = 'tzinfo'

class TimezoneMiddleware(object):
    """
    Determine what the most likely timezone is based on their IP address. If
    this cannot be determined use a local TZ proxy.
    """
    def __init__(self):
        if settings.DETECT_TZ is not True:
            raise MiddlewareNotUsed()

    def process_request(self, request):
        assert hasattr(request, 'session'), 'The TimezoneMiddleware class requires a session.'

        if TZ_ATTR not in request.session:
            ip_addr = request.META.get('REMOTE_ADDR' if 'HTTP_X_FORWARDED_FOR' not in request.environ \
                                        else 'HTTP_X_FORWARDED_FOR', None)
            result = 'local'
            if ip_addr is not None:
                result = rpc.geo.ipGeoData(ip_addr, _safe=True)
            request.session[TZ_ATTR] = result or 'local'

        tzname = request.session[TZ_ATTR]
        if tzname != 'local':
            messages.add_message(request, messages.INFO, 'Your timzone has been automatically set to %s' % tzname)
            request.autotz = pytz.timezone(tzname)
        else:
            request.autotz = LocalTimezone()
        return None