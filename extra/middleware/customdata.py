import re, fnmatch
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.views.generic.simple import redirect_to
from extra.rpc import rpc
import logging

logger = logging.getLogger(__name__)

MATCH_TYPES = {
    'hostname': re.compile(r':\/\/([^\.]+)\.', re.IGNORECASE),
    'firstslash': re.compile(r':\/\/[^\/]+\/([a-z0-9\-\_]+)\/?', re.IGNORECASE)
}

MATCH_CACHE_KEY = 'profile_id'

#Settings
CUSTOMDATA_WEBSITE_SLUG      = getattr(settings, 'CUSTOMDATA_WEBSITE_SLUG', None)
CUSOTMDATA_REDIRECT_ON_MISS  = getattr(settings, 'CUSOTMDATA_REDIRECT_ON_MISS', None)
CUSTOMDATA_USER_SLUG_PATTERN = getattr(settings, 'CUSTOMDATA_USER_SLUG_PATTERN', None)
CUSTOMDATA_HOSTNAMES         = getattr(settings, 'CUSTOMDATA_HOSTNAMES', None)

class CustomDataMiddleware(object):
    """
    Retrieve custom data from HP instances based on settings and current host or url and then
    make it available to a request context.
    """
    def __init__(self):
        self.match_type = MATCH_TYPES['hostname']
        if CUSTOMDATA_USER_SLUG_PATTERN is not None and CUSTOMDATA_USER_SLUG_PATTERN in MATCH_TYPES:
            self.match_type = MATCH_TYPES[CUSTOMDATA_USER_SLUG_PATTERN]

        if CUSTOMDATA_WEBSITE_SLUG is None:
            logger.info('Disabling customdata milddleware since there is no CUSTOMDATA_WEBSITE_SLUG setting.')
            raise MiddlewareNotUsed()

    def process_request(self, request):
        # Profile Matching Portion
        profile_key = self.get_profile_key(request)
        if profile_key is None:
            return self.redirect(request)
        logger.debug('Found profile key: %s' % profile_key)

        # If profile is matched, find it in cache or HP instance.
        cache_key = self._cache_key(CUSTOMDATA_WEBSITE_SLUG, profile_key)

        context = cache.get(cache_key)
        if context is None:
            logger.debug("Fetching Profile: %s from HP Instance" % profile_key)
            context = rpc.customdata.websiteData(CUSTOMDATA_WEBSITE_SLUG, profile_key, _safe=True)
            if context is None:
                context = {'match_success': False}
            else:
                context.update(match_success=True)
            cache.set(cache_key, context, 60)

        if context['match_success'] is False:
            return self.redirect(request)
        request._customdata = context

    def redirect(self, request):
        logger.debug('Could not successfully find customdata, attempting redirect.')
        if CUSOTMDATA_REDIRECT_ON_MISS is not None:
            redirect_url = reverse(CUSOTMDATA_REDIRECT_ON_MISS)
            if request.build_absolute_uri() != request.build_absolute_uri(redirect_url):
                return redirect_to(request, redirect_url)
        return None

    def get_profile_key(self, request):
        if MATCH_CACHE_KEY in request.session:
            return request.session.get(MATCH_CACHE_KEY)

        scopes = (request.GET, request.COOKIES)
        for scope in scopes:
            if MATCH_CACHE_KEY in scope:
                profile_key = scope.get(MATCH_CACHE_KEY)
                
                #Store this in the session and save immediately in-case of a redirect since it depends on the hostname
                request.session[MATCH_CACHE_KEY] = profile_key
                request.session.save()

                logger.debug('Found profile key: %s in cookie or query' % profile_key)
                return profile_key

        #Attempt URI match.
        attempt = True
        if CUSTOMDATA_HOSTNAMES:
            attempt = False
            for hostname in CUSTOMDATA_HOSTNAMES:
                if fnmatch.fnmatch(request.get_host(), hostname):
                    attempt = True
                    break

        if attempt is True:
            match = self.match_type.search(request.build_absolute_uri())
            if match:
                profile_key = match.groups()[0]

                #Store this in the session and save immediately in-case of a redirect since it depends on the hostname
                request.session[MATCH_CACHE_KEY] = profile_key
                request.session.save()

                logger.debug('Matched profile key: %s in the URI' % profile_key)
                return profile_key
        return None

    def _cache_key(self, site, user):
        return 'customdata-cache-%s-%s' % (site, user)


def context(request):
    return getattr(request, '_customdata', {})
