"""
If the session appears in the URL use it and try to save it as a cookie for
the next request.
"""
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.importlib import import_module

class URLSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        modify = False
        if settings.SESSION_COOKIE_NAME in request.GET:
            session_key = request.GET.get(settings.SESSION_COOKIE_NAME)
            modify = True
        else:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        request.session = engine.SessionStore(session_key)
        if modify is True:
            # This will force a cookie to be set
            request.session.modified = True
