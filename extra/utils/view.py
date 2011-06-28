from urllib import urlencode
from functools import partial
from decorator import decorator
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.context import RequestContext
from django.template import loader

def decorator_factory(decfac): # partial is functools.partial
    "decorator_factory(decfac) returns a one-parameter family of decorators"
    return partial(lambda df, param: decorator(partial(df, param)), decfac)

@decorator_factory
def render_to(template, func, request, *args, **kw):
    """
    A decorator for view functions which will accept a template parameter
    and then execute render_to_response. Views should return a context.

    @render_to('template')
    def view_func(request):
        return {'form': form}
    """
    output = func(request, *args, **kw)
    if isinstance(output, (list, tuple)):
        return render(request, output[1], output[0])
    elif isinstance(output, dict):
        return render(request, template, output)
    return output

def redirect(*args, **kwargs):
    """Creates a redirect response and accepts the same parameters as reverse.
    The reverse functionality can be overridden by passing in a named attributes 'url'
    keyword qs takes a dict and will create a query string"""
    if 'url' in kwargs:
        return HttpResponseRedirect(kwargs['url'])

    qs = kwargs.pop('qs', '')
    if qs:
        qs = '?'+urlencode(qs, True)

    return HttpResponseRedirect(reverse(*args, **kwargs)+qs)

def redirect_to_referrer(request, fallback=None, *args, **kwargs):
    """Creates an HttpResponse back to the referrer, if no referrer was specified
    then it uses the fallback kwarg."""
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if fallback:
        return redirect(fallback)
    return HttpResponseRedirect("/")

#:TODO: these _to_ function might be able to consolidate.
def render_to_string(request, template, dictionary=None):
    return loader.render_to_string(template, dictionary, context_instance=RequestContext(request))
