import logging, urlparse, urllib
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponseRedirect


logger = logging.getLogger(__name__)

DEBUG                 = getattr(settings, 'DEBUG')
#COMMONLY CHANGED OPTIONS
SSL_ENABLED           = getattr(settings, 'SSL_ENABLED', False) #Whether or not to actually use SSL
SSL_DOMAIN            = getattr(settings, 'SSL_DOMAIN', None) #If the SSL domain is different from current.
SSL_FULL_COVERAGE     = getattr(settings, 'SSL_FULL_COVERAGE', False) #Always redirect to SSL for any url.
#MORE FRINGE OPTIONS
SSL_FAKE              = getattr(settings, 'SSL_FAKE', DEBUG) #Just fake the redirects, good for debugging.
SSL_VIEW_KWARG        = getattr(settings, 'SSL_VIEW_KWARG', 'ssl') #If the view contains this kwarg, redirect.
SSL_SEND_SESSION      = getattr(settings, 'SSL_SEND_SESSION', False) #If the domain changes, append cookie data to the URL
SSL_USE_HTTPS         = getattr(settings, 'SSL_USE_HTTPS', True) #Whether to use https or stay on http.


class SSLRedirectMiddleware(object):
    def __init__(self):
        if SSL_ENABLED is False:
            logger.debug('Disabling sslredirect milddleware since SSL_ENABLED is False.')
            raise MiddlewareNotUsed()

    def process_request(self, request):
        if SSL_FULL_COVERAGE is True and not self._is_secure(request):
            logger.debug("SSL Full Coverage enabled, redirecting.")
            return self._redirect(request)
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        requires_ssl = view_kwargs.pop(SSL_VIEW_KWARG, None)

        if requires_ssl is not None and self._is_secure(request) != requires_ssl:
            logger.debug("Per View kwarg detected, redirecting.")
            return self._redirect(request, requires_ssl)
        return None

    def _is_secure(self, request):
        #For Testing
        if DEBUG == True and 'secure' in request.GET:
            return True
        
        if request.is_secure():
            return True
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'
        if 'HTTP_X_FORWARDED_PROTOCOL' in request.META:
            return request.META['HTTP_X_FORWARDED_PROTOCOL'] == 'https'
        return False

    def _redirect(self, request, secure=True):
        if request.method != 'GET':
            if DEBUG:
                raise RuntimeError('Can\'t perform an SSL redirect while '
                                   'maintaining POST data.  Please structure your views so that '
                                   'redirects only occur during GETs.')
            else:
                logger.error("Could not Redirect because of method %s. Domain: %s, Location: %s, Referrer: %s" % (request.method, request.get_host(), request.get_full_path(), request.META.get('HTTP_REFERER', 'None')))
            return None

        scheme = 'https' if secure and SSL_USE_HTTPS else 'http'
        domain = SSL_DOMAIN or request.get_host()
        path = request.path
        query_string = urlparse.parse_qs(request.META['QUERY_STRING'], keep_blank_values=True)
        if DEBUG:
            query_string.update(secure='yes')

        if SSL_SEND_SESSION and domain != request.get_host():
            if hasattr(request, 'session') and request.session._session_key is not None:
                cookie_name = getattr(settings, 'SESSION_COOKIE_NAME')
                query_string.update(**{cookie_name: request.session._session_key})
                logger.debug("Adding Session to Redirect: %s" % request.session._session_key)
            else:
                logger.info("Attempted to send the session in the URL however sessions are not enabled or there is no session available.")

        #Build URL
        newurl = urlparse.urlunsplit((scheme, domain, path, urllib.urlencode(query_string, doseq=True), ''))

        if SSL_FAKE is True:
            logger.info("We are redirecting to (%s), but not really since SSL_FAKE is True (by default it is the same value as DEBUG)." % newurl)
            return None
        logger.debug("Redirecting to: %s" % newurl)
        return HttpResponseRedirect(newurl)
