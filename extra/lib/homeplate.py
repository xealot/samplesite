"""
Expose the HomePlateHQ API Endpoints in expressive Python Syntax.
"""
import calendar, datetime, urllib2
import tz

try:
    import simplejson as json
except ImportError: 
    import json


def datetime_json_default(obj):
    """
    The primary role of this function is to convert datetime instances
    into a JSON representation of a UTC datetime.
    """
    if type(obj) is datetime.date:
        #Convert to datetime
        obj = datetime.datetime.combine(obj, datetime.time())
    if type(obj) is datetime.datetime:
        #If object is naive, replace the lack of a timezone with the locally derived timezone.
        if obj.tzinfo is None or obj.tzinfo.utcoffset(obj) is None:
            obj = obj.replace(tzinfo=tz.LocalTimezone(obj))
        utc_obj = obj.astimezone(tz.UTC())
        return {'__complex__': 'datetime',
                'tz': 'UTC',
                'epoch': calendar.timegm(utc_obj.timetuple()),
                'iso8601': utc_obj.isoformat(' ')}
    raise TypeError()

def datetime_json_object_hook(obj):
    if '__complex__' in obj:
        return datetime.datetime.fromtimestamp(obj['epoch'], tz.UTC())
    return obj


class HomeplateException(Exception): pass
class SafeHomeplateException(HomeplateException): pass


class JSONRPCHandler(object):
    """
    New Request
    handler = JSONRPCRequest(url)
    result = handler.authentication.checkPassword(args or kwargs)
    result = handler[weird-named-function](args or kwargs)
    results = handler.multi(
        ('name.of.function', args or kwargs),
        ('name.of.function', args or kwargs),
    )
    """
    RPC_VER = '2.0'

    def __init__(self, url, quiet=False):
        self.url = url
        self.id = 100
        self.quiet = quiet

    def __getattr__(self, name):
        return JSONRPCRequest(self, [name])

    def call(self, name, params):
        name = self.join_namespace(name)
        request = urllib2.Request(self.url,
                                  self._encode(self._create_call(name, params)),
                                  self.http_headers())

        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            print 'RPC ERROR', self.url, request.data, e.read()
            raise HomeplateException('HP Returned an Error Code of: %s' % e.code)
        except urllib2.URLError, e:
            raise HomeplateException('HTTP Request Failed: %s' % e.reason)

        json_response = response.read()
        result = self._decode(json_response)

        if 'result' in result:
            return result['result']
        elif 'error' in result:
            #print json_response
            raise SafeHomeplateException(result['error']['reason'])
        else:
            #print json_response
            raise SafeHomeplateException('Invalid Response')

    def multi(self, invocations):
        print invocations
        pass

    def join_namespace(self, name):
        return '.'.join(name)

    def http_headers(self, **headers):
        headers.update({
            'Content-Type': 'application/json'
        })
        return headers

    def _encode(self, object):
        return json.dumps(object, default=datetime_json_default, indent=4)

    def _decode(self, string):
        return json.loads(string, object_hook=datetime_json_object_hook)

    def _create_call(self, name, params):
        return dict(
            id=self.id,
            jsonrpc=self.RPC_VER,
            method=name,
            params=params
        )


class JSONRPCRequest(object):
    """
    Transparently replaces Handler class after initial getattr.
    """
    def __init__(self, handler, current):
        self.handler = handler
        self.current = current

    def __getattr__(self, name):
        self.current.append(name)
        return self
    
    def __call__(self, *a, **kw):
        safe = kw.pop('_safe', False)
        assert (bool(a) ^ bool(kw)) or (not bool(a) and not bool(kw)), "Mixing keyword arguments and non is not allowed"
        try:
            return self.handler.call(self.current, (a or kw))
        except SafeHomeplateException as e:
            if safe is True:
                return None
            raise e


class HPRPCHandler(JSONRPCHandler):
    """
    Adding authorization into JSONRPC class specific to Homeplate
    """
    def __init__(self, api_token, url):
        self.token = api_token
        super(HPRPCHandler, self).__init__(url)

    def http_headers(self):
        return super(HPRPCHandler, self).http_headers(**{'X-Authorization': self.token})
