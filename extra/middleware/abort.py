from django.http import HttpResponseRedirect

#301: Moved Perm
#302: Found

def abort(code_or_url, permanent=False):
    if not isinstance(code_or_url, (int, long)):
        raise HttpRedirectException(code_or_url, 301 if permanent else 302)


class HttpRedirectException(Exception):
    pass


class AbortMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, HttpRedirectException):
            return HttpResponseRedirect(exception.args[0])