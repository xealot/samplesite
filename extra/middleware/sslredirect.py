from django.conf import settings
from django.http import HttpResponsePermanentRedirect
import re
import logging

logger = logging.getLogger(__name__)


SSL = 'SSL'
ACTIVE_RETURN = getattr(settings, 'SSL_ACTIVE_RETURN', False)
ALWAYS_USE_SSL = getattr(settings, 'SSL_ALWAYS_ENABLED', False)
USE_SSL = getattr(settings, 'SSL_ENABLED', ALWAYS_USE_SSL)
SSL_URLS = tuple([re.compile(url) for url in getattr(settings, 'SSL_URLS', ())])

class SSLRedirectMiddleware:
    
    def process_request(self, request):
        """ If the SSL_URLS setting was used check for a match in the 
        RE's of the setting. If a match occurs and we're not secure, secure it.
        """
        request._needs_ssl = False if ACTIVE_RETURN else None
        if not SSL_URLS:
            return
        secure = False
        for url in SSL_URLS:
            if url.match(request.path):
                secure = True
                break
        if not secure == self._is_secure(request):
            request._needs_ssl = True
            #return self._redirect(request, secure)
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        request._needs_ssl = view_kwargs.pop(SSL, request._needs_ssl)

        if ALWAYS_USE_SSL:
            request._needs_ssl = True

        if request._needs_ssl is not None and request._needs_ssl != self._is_secure(request):
            return self._redirect(request, request._needs_ssl)
        return None

    def _is_secure(self, request):
        #For Testing
        if settings.DEBUG == True and 'secure' in request.GET:
            return True
        
        if request.is_secure():
            return True
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'
        return False

    def _redirect(self, request, secure):
        protocol = secure and 'https' or 'http'
        newurl = '%s://%s%s' % (protocol, request.get_host(), request.get_full_path())
        if USE_SSL is False:
            logger.info("We are redirecting to (%s), but not really since USE_SSL is disabled." % protocol)
            return None
        if request.method == 'GET':
            return HttpResponsePermanentRedirect(newurl)
        else:
            if settings.DEBUG:
                raise RuntimeError('Can\'t perform an SSL redirect while '
                                   'maintaining POST data.  Please structure your views so that '
                                   'redirects only occur during GETs.')
            else:
                logger.error("Could not Redirect to (%s) because of method %s. Domain: %s, Location: %s, Referrer: %s" % (secure, request.method, request.get_host(), request.get_full_path(), request.META.get('HTTP_REFERER', 'None')))
        

