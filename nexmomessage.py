import urllib
import urllib2
import urlparse
import json

BASEURL = "https://rest.nexmo.com"

class NexmoException(Exception):
    pass

class NexmoMessage:

    def __init__(self, details):
        self.sms = details
        self.sms.setdefault('type', 'text')
        self.sms.setdefault('server', BASEURL)
        self.sms.setdefault('reqtype', 'json')

        self.smstypes = [
            'text',
            'binary',
            'wappush',
            'vcal',
            'vcard',
            'unicode'
        ]
        self.apireqs = [
            'balance',
            'pricing',
            'numbers',
            'search',
            'buy',
            'cancel',
            'update'
        ]
        self.reqtypes = [
            'json',
            'xml'
        ]
        self.request = None

    def url_fix(self, s, charset='utf-8'):
        if isinstance(s, unicode):
            s = s.encode(charset, 'ignore')
        scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
        path = urllib.quote(path, '/%')
        qs = urllib.quote_plus(qs, ':&=')
        return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

    def set_text_info(self, text):
        # automatically transforms msg to text SMS
        self.sms['type'] = 'text'
        self.sms['text'] = text

    def set_bin_info(self, body, udh):
        # automatically transforms msg to binary SMS
        self.sms['type'] = 'binary'
        self.sms['body'] = body
        self.sms['udh'] = udh

    def set_wappush_info(self, title, url, validity=False):
        # automatically transforms msg to wappush SMS
        self.sms['type'] = 'wappush'
        self.sms['title'] = title
        self.sms['url'] = url
        self.sms['validity'] = validity

    def set_vcal_info(self, vcal):
        # automatically transforms msg to vcal SMS
        self.sms['type'] = 'vcal'
        self.sms['vcal'] = vcal

    def set_vcard_info(self, vcard):
        # automatically transforms msg to vcard SMS
        self.sms['type'] = 'vcard'
        self.sms['vcard'] = vcard

    def check_sms(self):
        """ http://www.nexmo.com/documentation/index.html#request
            http://www.nexmo.com/documentation/api/ """
        # mandatory parameters for all requests
        if not self.sms.get('username') or not self.sms.get('password'):
            raise NexmoException("No username or password")

        # API requests handling
        if self.sms['type'] in self.apireqs:
            if self.sms['type'] == 'balance' or self.sms['type'] == 'numbers':
                return True
            elif self.sms['type'] in ['pricing', 'search'] and not self.sms.get('country'):
                raise NexmoException("Pricing/search needs country")
            elif self.sms['type'] in ['buy'] and (not self.sms.get('country') or not self.sms.get('msisdn')):
                raise NexmoException("Buy needs country and msisdn")
            elif (self.sms['type'] == 'cancel' and
                  (not self.sms.get('country') or not self.sms.get('msisdn'))):
                raise NexmoException("Cancel needs country and msisdn")
            elif self.sms['type'] in ['update'] and (not self.sms.get('country') or not self.sms.get('msisdn') or not self.sms.get('moHttpUrl')):
                raise NexmoException("Update needs country, msisdn, and moHttpUrl")
            return True
        # SMS logic, check Nexmo doc for details
        elif self.sms['type'] not in self.smstypes:
            raise NexmoException("Invalid Type")
        elif self.sms['type'] == 'text' and not self.sms.get('text'):
            raise NexmoException("Missing Text")
        elif self.sms['type'] == 'binary' and (not self.sms.get('body') or \
                not self.sms.get('udh')):
            raise NexmoException("Missing Binary")
        elif self.sms['type'] == 'wappush' and (not self.sms.get('title') or \
                not self.sms.get('url')):
            raise NexmoException("Missing title/url")
        elif self.sms['type'] == 'vcal' and not self.sms.get('vcal'):
            raise NexmoException("Missing vcal")
        elif self.sms['type'] == 'vcard' and not self.sms.get('vcard'):
            raise NexmoException("Missing vcard")
        elif not self.sms.get('from') or not self.sms.get('to'):
            raise NexmoException("Missing from or to")
        return True

    def build_request(self):
        # check SMS logic
        if not self.check_sms():
            raise NexmoException("Invalid SMS")
        elif self.sms['type'] in self.apireqs:
            # basic API requests
            # balance
            if self.sms['type'] == 'balance':
                self.request = "%s/account/get-balance/%s/%s" % (BASEURL,
                    self.sms['username'], self.sms['password'])
            # pricing
            elif self.sms['type'] == 'pricing':
                self.request = "%s/account/get-pricing/outbound/%s/%s/%s" \
                    % (BASEURL, self.sms['username'], self.sms['password'],
                       self.sms['country'])
            # numbers
            elif self.sms['type'] == 'numbers':
                self.request = "%s/account/numbers/%s/%s/?" % (BASEURL,
                    self.sms['username'], self.sms['password'])

                attribs = []
                for attrib in ['size', 'index', 'pattern']:
                    if attrib in self.sms:
                        attribs.append("%s=%s" % (attrib, self.sms[attrib]))

                self.request += '&'.join(attribs)
            # search
            elif self.sms['type'] == 'search':
                self.request = "%s/number/search/%s/%s/%s" \
                    % (BASEURL, self.sms['username'], self.sms['password'],
                       self.sms['country'])
            # buy
            elif self.sms['type'] == 'buy':
                self.request = "%s/number/buy/%s/%s/%s/%s" \
                    % (BASEURL, self.sms['username'], self.sms['password'],
                       self.sms['country'], self.sms['msisdn'])
            # Cancel a number that was previously bought.
            elif self.sms['type'] == 'cancel':
                self.request = ("%s/number/cancel/%s/%s/%s/%s" % (
                    BASEURL, self.sms['username'], self.sms['password'],
                    self.sms['country'], self.sms['msisdn']))
            # update
            elif self.sms['type'] == 'update':
                self.request = "%s/number/update/%s/%s/%s/%s/?" \
                    % (BASEURL, self.sms['username'], self.sms['password'],
                       self.sms['country'], self.sms['msisdn'])

                # we assume these have been properly escaped right now
                optional = ['moHttpUrl', 'moSmppSysType', 'voiceCallbackType', 'voiceCallbackValue']
                params = "&".join(["%s=%s" % (param, self.sms[param]) for param in optional if param in self.sms])
                self.request += params

            return self.request
        else:
            # standard requests
            if self.sms['reqtype'] not in self.reqtypes:
                raise NexmoException("Invalid reqtype")
            params = self.sms.copy()
            params.pop('reqtype')
            params.pop('server')
            server = "%s/sms/%s" % (BASEURL, self.sms['reqtype'])
            self.request = server + "?" + urllib.urlencode(params)
            return self.request
        return False

    def get_details(self):
        return self.sms

    def send_request(self):
        if not self.build_request():
            raise NexmoException("Failed to build")
        if self.sms['reqtype'] == 'json':
            return self.send_request_json(self.request)
        elif self.sms['reqtype'] == 'xml':
            return self.send_request_xml(self.request)

    def send_request_json(self, request):
        url = request
        header = {'Accept' : 'application/json'}
        req = None
        # POST to the URL if we're buying, updating or canceling.  Otherwise
        # GET.
        if (self.sms['type'] in ['buy', 'update', 'cancel']):
            req = urllib2.Request(url, urllib.urlencode({}), header)
        else:
            req = urllib2.Request(url, None, header)

        # Some methods don't return json.
        if (self.sms['type'] in ['buy', 'update', 'cancel']):
            return {'code' : urllib2.urlopen(req).getcode()}
        else:
            return json.load(urllib2.urlopen(req))

    def send_request_xml(self, request):
        return "XML request not implemented yet."
