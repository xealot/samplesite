"""
Abstraction for testing and retrieving cleaned 
US addresses.
"""
import urllib, urllib2, collections
from functools import partial
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

Address = collections.namedtuple('USAddress', 'street city state zip zip4 unit')

#USPS_BASE_URL = "http://testing.shippingapis.com/ShippingAPITest.dll"
USPS_BASE_URL = "http://production.shippingapis.com/ShippingAPI.dll"

def fetch_text(element, name):
    subnode = element.find(name)
    if subnode is None:
        return ''
    return subnode.text

class USPSAddressCheck(object):
    API_NAME = 'Verify'
    
    def __init__(self, usps_user, usps_password):
        self.user = usps_user
        self.auth = usps_password
    
    def __send(self, xml):
        xml_string = etree.tostring(xml)
        request = urllib2.Request(USPS_BASE_URL, urllib.urlencode({'API': self.API_NAME, 'XML': xml_string}))

        try:
            response = urllib2.urlopen(request, timeout=5)
        except urllib2.HTTPError as e:
            raise e
        except urllib2.URLError as e:
            raise e

        xml_response = etree.fromstring(response.read())

        response = {}
        for address in xml_response:
            id = address.get('ID')
            if address.find('Error') is not None:
                response[id] = None
            else:
                response[id] = Address(**dict(
                    street=fetch_text(address, 'Address2'),
                    city=fetch_text(address, 'City'),
                    state=fetch_text(address, 'State'),
                    zip=fetch_text(address, 'Zip5'),
                    zip4=fetch_text(address, 'Zip4'),
                    unit=fetch_text(address, 'Address1')
                ))
        return response

    def check_address(self, street='', city='', state='', zip='', unit=''):
        xml = E.AddressValidateRequest(
            E.Address(
              E.Address1(unit),
              E.Address2(street),
              E.City(city),
              E.State(state),
              E.Zip5(zip),
              E.Zip4(),
              ID='0',
            ),
            USERID=self.user
        )

        #For a single call, just return ID=0.
        return self.__send(xml)['0']
        

class ElementMaker(object):
    """
    This is a direct copy (minus some things) of the LXML implementation
    of the E-Factory.
    """
    def __init__(self, typemap=None,
                 namespace=None, nsmap=None, makeelement=None):
        if namespace is not None:
            self._namespace = '{' + namespace + '}'
        else:
            self._namespace = None

        if nsmap:
            self._nsmap = dict(nsmap)
        else:
            self._nsmap = None

        if makeelement is not None:
            assert callable(makeelement)
            self._makeelement = makeelement
        else:
            self._makeelement = etree.Element

        # initialize type map for this element factory

        if typemap:
            typemap = typemap.copy()
        else:
            typemap = {}
        
        def add_text(elem, item):
            if len(elem):
                elem[-1].tail = (elem[-1].tail or "") + item
            else:
                elem.text = (elem.text or "") + item
        if str not in typemap:
            typemap[str] = add_text
        if unicode not in typemap:
            typemap[unicode] = add_text

        def add_dict(elem, item):
            attrib = elem.attrib
            for k, v in item.items():
                if isinstance(v, basestring):
                    attrib[k] = v
                else:
                    attrib[k] = typemap[type(v)](None, v)
        if dict not in typemap:
            typemap[dict] = add_dict

        self._typemap = typemap
        
    def __call__(self, tag, *children, **attrib):
        get = self._typemap.get

        if self._namespace is not None and tag[0] != '{':
            tag = self._namespace + tag
        #I HAVE ADDED THIS TO BE MORE COMPATIBLE WITH THE PYTHON ETREE
        if self._nsmap is not None:
            elem = self._makeelement(tag, nsmap=self._nsmap)
        else:
            elem = self._makeelement(tag)
            
        if attrib:
            get(dict)(elem, attrib)

        for item in children:
            if callable(item):
                item = item()
            t = get(type(item))
            if t is None:
                if etree.iselement(item):
                    elem.append(item)
                    continue
                raise TypeError("bad argument type: %r" % item)
            else:
                v = t(elem, item)
                if v:
                    get(type(v))(elem, v)

        return elem

    def __getattr__(self, tag):
        return partial(self, tag)

E = ElementMaker()
