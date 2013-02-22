import json
from hashlib import md5
from urllib import urlencode

import requests
try:
    from tornado.httpclient import AsyncHTTPClient, HTTPRequest
    has_async = True
except ImportError:
    has_async = False

from .generated import BaseClient


API_URL = 'http://ws.audioscrobbler.com/2.0/'
AUTH_URL = 'http://www.last.fm/api/auth/?api_key={key}&cb={callback}'


ERRORS = {
    # http://www.last.fm/api/errorcodes
    1: 'This error does not exist',
    2: 'Invalid service -This service does not exist',
    3: 'Invalid Method - No method with that name in this package',
    4: 'Authentication Failed - You do not have permissions to access the service',
    5: 'Invalid format - This service doesn\'t exist in that format',
    6: 'Invalid parameters - Your request is missing a required parameter',
    7: 'Invalid resource specified',
    8: 'Operation failed - Most likely the backend service failed. Please try again.',
    9: 'Invalid session key - Please re-authenticate',
    10: 'Invalid API key - You must be granted a valid key by last.fm',
    11: 'Service Offline - This service is temporarily offline. Try again later.',
    12: 'Subscribers Only - This station is only available to paid last.fm subscribers',
    13: 'Invalid method signature supplied',
    14: 'Unauthorized Token - This token has not been authorized',
    15: 'This item is not available for streaming.',
    16: 'The service is temporarily unavailable, please try again.',
    17: 'Login: User requires to be logged in',
    18: 'Trial Expired - This user has no free radio plays left. Subscription required.',
    19: 'This error does not exist',
    20: 'Not Enough Content - There is not enough content to play this station',
    21: 'Not Enough Members - This group does not have enough members for radio',
    22: 'Not Enough Fans - This artist does not have enough fans for for radio',
    23: 'Not Enough Neighbours - There are not enough neighbours for radio',
    24: 'No Peak Radio - This user is not allowed to listen to radio during peak usage',
    25: 'Radio Not Found - Radio station not found',
    26: 'API Key Suspended - This application is not allowed to make requests to the web services',
    27: 'Deprecated - This type of request is no longer supported',
    29: 'Rate Limit Exceeded - Your IP has made too many requests in a short period, exceeding our API guidelines',
}


class LastfmAPIError(Exception):

    def __init__(self, error, message):
        self.message = '[%s %s] %s' % (
            error,
            ERRORS.get(error, 'unknown error'),
            message
        )
        self.code = error
        self.msg = message

    def __str__(self):
        return self.message


class LastfmClient(BaseClient):

    api_key = None
    api_secret = None

    def __init__(self, api_key=None, api_secret=None, session_key=None):
        super(LastfmClient, self).__init__()

        if api_key:
            self.api_key = api_key
        if api_secret:
            self.api_secret = api_secret
        self.session_key = session_key

        assert self.api_key and self.api_secret, 'Missing API key or secret.'

    def get_auth_url(self, callback_url):
        return AUTH_URL.format(key=self.api_key, callback=callback_url)

    def _get_params(self, method, params, auth):

        if params is None:
            params = {}

        defaults = {
            'format': 'json',
            'api_key': self.api_key,
            'method': method,
        }

        params.update(defaults)
        params = {k: v for k, v in params.items()
                  if v is not None and k != 'callback'}

        getting_session = method == 'auth.getSession'
        auth = auth or (method == 'user.getInfo' and 'user' not in params)
        if auth or getting_session:
            if not getting_session:
                assert self.session_key, 'Missing session key.'
                params['sk'] = self.session_key
            params['api_sig'] = self._get_sig(params)
        return params

    def _get_sig(self, params):
        exclude = {'format', 'callback'}
        sig = ''.join(k + unicode(v).encode('utf8') for k, v
                      in sorted(params.items()) if k not in exclude)
        sig += self.api_secret
        hash = md5(sig).hexdigest()
        return hash

    def _process_data(self, data):
        if 'error' in data:
            raise LastfmAPIError(**data)
        if isinstance(data, dict):
            keys = data.keys()
            if len(keys) == 1:
                return data[keys[0]]
        return data

    def call(self, http_method, method, auth, params):
        params = self._get_params(method, params, auth)
        data = requests.request(http_method, API_URL, params=params).json
        return self._process_data(data)


class AsyncLastfmClient(LastfmClient):

    def __init__(self, api_key=None, api_secret=None, session_key=None):
        super(AsyncLastfmClient, self).__init__(
            api_key, api_secret, session_key)
        if not has_async:
            raise RuntimeError('You need to install tornado.')

    @property
    def _async_client(self):
        return AsyncHTTPClient()

    def call(self, http_method, method, auth, params):

        url = API_URL

        callback = params.pop('callback')
        params = self._get_params(method, params, auth)
        params = urlencode({k: unicode(v).encode('utf8')
                            for k, v in params.items()})
        if http_method == 'POST':
            body = params
        else:
            body = None
            url = url + '?' + params

        def on_finish(response):
            data = self._process_data(json.loads(response.body))
            if callback:
                callback(data)

        self._async_client.fetch(
            url, method=http_method,
            body=body, callback=on_finish)
