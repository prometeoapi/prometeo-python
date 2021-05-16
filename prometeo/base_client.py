from six.moves.urllib.parse import urljoin
import requests

from prometeo import exceptions


class BaseClient(object):
    """
    Base client class to make api calls
    """

    ENVIRONMENTS = {}

    session_class = None

    def make_request(self, method, url, *args, **kwargs):
        base_url = self.ENVIRONMENTS[self._environment]
        full_url = urljoin(base_url, url)
        headers = {
            'X-API-Key': self._api_key,
        }
        return self._client_session.request(
            method, full_url, headers=headers, *args, **kwargs
        )

    def on_response(self, response_data):
        """
        Called after every 200 response
        """
        pass

    def call_api(self, method, url, *args, **kwargs):
        """
        Calls an API endpoint, using the configured api key and environment.

        :param method: The HTTP method to use (``GET``, ``POST``, etc)
        :type method: str

        :param url: The url to call (without the environment's domain)
        :type url: str

        :rtype: JSON data as a python object.
        """
        response = self.make_request(method, url, *args, **kwargs)
        try:
            data = response.json()
        except ValueError:
            data = {}
        if response.status_code == 400:
            raise exceptions.BadRequestError(data.get('message'))
        elif response.status_code == 401:
            raise exceptions.UnauthorizedError(data.get('message'))
        elif response.status_code == 403 and data.get('status') != 'wrong_credentials':
            raise exceptions.ForbiddenError(data.get('message'))
        elif response.status_code == 404:
            raise exceptions.NotFoundError(data.get('message'))
        elif response.status_code == 500:
            raise exceptions.InternalAPIError(data.get('message', response.text))
        elif response.status_code == 503:
            raise exceptions.ProviderUnavailableError(data.get('message'))
        self.on_response(data)
        return data

    def get_session(self, session_key):
        """
        Restore a session from its session key

        :param session_key: The session key
        :type session_key: str

        :rtype: :class:`Session`
        """
        return self.session_class(self, None, session_key)

    def __init__(self, api_key, environment):
        self._api_key = api_key
        if environment not in self.ENVIRONMENTS:
            valid_envs = ", ".join(self.ENVIRONMENTS.keys())
            raise exceptions.ClientError(
                'Invalid environment "{}", options are {}'.format(
                    environment, valid_envs
                )
            )
        self._environment = environment
        self._client_session = requests.Session()


class Download(object):
    """
    Represents a downloadable file, like an xml bill or pdf document
    """

    def __init__(self, client, url):
        self._client = client
        self.url = url

    def get_file(self):
        """
        Downloads the file and returns its contents.

        :rtype: bytes
        """
        resp = self._client.make_request('GET', self.url)
        return resp.content
