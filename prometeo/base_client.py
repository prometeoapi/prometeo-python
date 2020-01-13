from six.moves.urllib.parse import urljoin
import requests

from prometeo import exceptions


class BaseClient(object):

    ENVIRONMENTS = {}

    def make_request(self, method, url, *args, **kwargs):
        base_url = self.ENVIRONMENTS[self._environment]
        full_url = urljoin(base_url, url)
        headers = {
            'X-API-Key': self._api_key,
        }
        return self._client_session.request(
            method, full_url, headers=headers, *args, **kwargs
        )

    def call_api(self, method, url, *args, **kwargs):
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
        return data

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
