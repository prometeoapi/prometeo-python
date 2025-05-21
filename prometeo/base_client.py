from six.moves.urllib.parse import urljoin
import httpx

from typing import Dict

from prometeo import exceptions, utils


class BaseClient(object):
    """
    Base client class to make api calls
    """

    ENVIRONMENTS = {}

    session_class = None

    def __init__(
        self,
        api_key,
        environment,
        raw_responses=False,
        proxy=None,
        *args,
        **kwargs
    ):
        self._api_key = api_key
        if environment not in self.ENVIRONMENTS:
            valid_envs = ", ".join(self.ENVIRONMENTS.keys())
            raise exceptions.ClientError(
                'Invalid environment "{}", options are {}'.format(
                    environment, valid_envs
                )
            )
        self._environment = environment
        self._client_session = httpx.AsyncClient(proxy=proxy, *args, **kwargs)
        self._raw_responses = raw_responses

    def _pop_nulls(self, data: Dict) -> Dict:
        return {k: v for k, v in data.items() if v is not None}

    @utils.adapt_async_sync
    async def make_request(
        self,
        method,
        url,
        headers=None,
        data=None,
        *args,
        **kwargs
    ):
        base_url = self.ENVIRONMENTS[self._environment]
        full_url = urljoin(base_url, url)
        headers = headers or {}
        if data:
            data = self._pop_nulls(data)
        headers["X-API-Key"] = self._api_key
        return await self._client_session.request(
            method, full_url, headers=headers, data=data, *args, **kwargs
        )

    def on_response(self, response_data):
        """
        Called after every 200 response
        """
        pass

    def on_error(self, response, data):
        """
        Check errors on response
        """
        if response.status_code == 400:
            raise exceptions.BadRequestError(data.get("message"))
        elif response.status_code == 401:
            raise exceptions.UnauthorizedError(data.get("message"))
        elif response.status_code == 403 and data.get("status") != "wrong_credentials":
            raise exceptions.ForbiddenError(data.get("message"))
        elif response.status_code == 404:
            raise exceptions.NotFoundError(data.get("message"))
        elif response.status_code == 500:
            raise exceptions.InternalAPIError(data.get("message", response.text))
        elif response.status_code == 503:
            raise exceptions.ProviderUnavailableError(data.get("message"))

    @utils.adapt_async_sync
    async def call_api(self, method, url, headers=None, *args, **kwargs):
        """
        Calls an API endpoint, using the configured api key and environment.

        :param method: The HTTP method to use (``GET``, ``POST``, etc)
        :type method: str

        :param url: The url to call (without the environment's domain)
        :type url: str

        :rtype: JSON data as a python object.
        """
        response = await self.make_request(method, url, headers, *args, **kwargs)
        if not self._raw_responses:
            try:
                data = response.json()
            except ValueError:
                data = {}
            self.on_error(response, data)
            self.on_response(data)
            return data
        return response

    def get_session(self, session_key=""):
        """
        Restore a session from its session key
        :param session_key: The session key
        :type session_key: str

        :rtype: :class:`Session`
        """
        return self.session_class(self, None, session_key)

    def new_session(self):
        """
        Creates a new session

        :param session_key: The session key
        :type session_key: str

        :rtype: :class:`Session`
        """
        return self.session_class(self, None, "")


class Download(object):
    """
    Represents a downloadable file, like an xml bill or pdf document
    """

    def __init__(self, client, url):
        self._client = client
        self.url = url

    @utils.adapt_async_sync
    async def get_file(self):
        """
        Downloads the file and returns its contents.

        :rtype: bytes
        """
        resp = await self._client.make_request("GET", self.url)
        return resp.content
