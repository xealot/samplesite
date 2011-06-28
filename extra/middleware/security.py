from urlparse import urlsplit, urlunsplit
from urllib import urlencode
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

LOGIN = 'LOGIN'
REQUIRES = 'REQUIRES'

login_url_parsed = urlsplit(settings.LOGIN_URL)

class AccessCheckMiddleware(object):
    
    def process_request(self, request):
        assert hasattr(request, 'session'), 'The SecurityMiddleware class requires a session.'
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        login = view_kwargs.pop(LOGIN, False)
        requires = view_kwargs.pop(REQUIRES, ())
        
        if login is True and not request.user.is_authenticated():
            messages.add_message(request, messages.INFO, 'Looks like your session expired, please login again.')
            return self._redirect_to_login(request, getattr(settings, 'ENABLE_SSL', False))
        
        if requires:
            #:TODO: move decision of whether to call has_perm or has_perms to BaseUser model
            requires = [requires] if isinstance(requires, basestring) else requires
            if not request.user.has_perms(requires):
                messages.add_message(request, messages.INFO, """You are not allowed to access this area, please 
                    login as a user with the proper permissions or contact an administrator 
                    if you think you are receiving this message in error.""")
                return self._redirect_to_login(request, getattr(settings, 'ENABLE_SSL', False))                
        return None

    def _redirect_to_login(self, request, secure):
        protocol = 'https' if secure is True else 'http'
        query = {'next': request.get_full_path(), 'skip_check': 1}
        return HttpResponseRedirect(urlunsplit([protocol, request.get_host(), settings.LOGIN_URL, urlencode(query), None]))


class ExpirePasswordMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), 'The SecurityMiddleware class requires a session.'
        if request.user.is_authenticated() and request.user.force_change and request.path != reverse("changepass"):
            messages.add_message(request, messages.INFO, u'Your password is expired, you must change it before continuing.')
            return HttpResponseRedirect(reverse("changepass"))
        return None
    