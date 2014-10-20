from hashlib import md5

from .api import BaseClient
from .exceptions import EXCEPTIONS_BY_CODE


API_URL = 'http://ws.audioscrobbler.com/2.0/'
AUTH_URL = 'http://www.last.fm/api/auth/?api_key={key}&cb={callback}'


class LastfmClient(BaseClient):
    """
    Blocking Last.fm client.

    Uses ``requests`` to perform HTTP requests.

    """

    api_key = None
    api_secret = None

    def __init__(self, api_key=None, api_secret=None, session_key=None):
        """
        :param api_key: Last.fm API key
        :param api_secret: Last.fm API secret
        :param session_key: Last.fm API user session key

        """
        super(LastfmClient, self).__init__()

        if api_key:
            self.api_key = api_key

        if api_secret:
            self.api_secret = api_secret

        self.session_key = session_key

        assert self.api_key and self.api_secret, 'Missing API key or secret.'

    def get_auth_url(self, callback_url):
        """
        Return a URL where the user can confirm this app.

        :param callback_url: Where the user should be redirected once he
                             confirms the request.

        """
        return AUTH_URL.format(key=self.api_key, callback=callback_url)

    def call(self, http_method, method, auth, params):
        """Perform the actual HTTP call and return a response data `dict`.

        :param http_method: the name of the HTTP method
        :type http_method: str

        :param method: the name of the Last.fm API method
        :type method: str

        :param auth: is authentication/signature needed?
        :type auth: bool

        :param params: parameters passed as GET or POST data.
        :type params: dict

        """
        try:
            import requests
        except ImportError:
            raise RuntimeError(
                'You need to install requests `pip install '
                'requests` for LastfmClient to work.'
            )
        params = self._get_params(method, params, auth)
        data = requests.request(http_method, API_URL, params=params).json()
        return self._process_response_data(data)

    def _get_params(self, method, params, auth):
        """Return a `dict` of final request parameters."""
        if params is None:
            params = {}

        defaults = {
            'format': 'json',
            'api_key': self.api_key,
            'method': method,
        }

        params.update(defaults)
        params = {k.rstrip('_'): v for k, v in params.items()
                  if v is not None and k != 'callback'}

        getting_session = method == 'auth.getSession'

        needs_auth = auth or getting_session or (
            method == 'user.getInfo' and 'user' not in params)

        if needs_auth:
            if not getting_session:
                assert self.session_key, 'Missing session key.'
                params['sk'] = self.session_key

            params['api_sig'] = self._get_sig(params)

        return params

    def _get_sig(self, params):
        """Create a signature as per http://www.last.fm/api/authspec#8."""
        exclude = {'format', 'callback'}
        sig = ''.join(k + unicode(v).encode('utf8') for k, v
                      in sorted(params.items()) if k not in exclude)
        sig += self.api_secret
        return md5(sig).hexdigest()

    def _process_response_data(self, data):
        """
        :param data: the parsed response JSON data
        :type data: dict

        """
        if 'error' in data:
            error_code, message = int(data['error']), data['message']
            raise EXCEPTIONS_BY_CODE[error_code].__call__(
                code=error_code,
                message=message
            )

        if isinstance(data, dict):
            keys = data.keys()
            if len(keys) == 1:
                return data[keys[0]]

        return data

