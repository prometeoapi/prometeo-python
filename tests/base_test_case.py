import json
import asynctest

from prometeo import Client
import httpx
from six.moves.urllib.parse import parse_qs, urlparse


class BaseTestCase(asynctest.TestCase):
    def setUp(self):
        self.client = Client("test_key")

    @property
    def module_name(self):
        return self.__class__.__module__.split(".")[1]

    def load_json(self, file_name):
        with open(f"tests/fixtures/{self.module_name}/{file_name}.json") as f:
            return json.load(f)

    def mock_get_request(
        self, mocker, url, fixture_name=None, json=None, status_code=200, **kwargs
    ):
        if not fixture_name:
            mocker.get(url).mock(
                return_value=httpx.Response(status_code, json=json, **kwargs)
            )
        else:
            mocker.get(url).mock(
                return_value=httpx.Response(
                    status_code, json=self.load_json(fixture_name)
                )
            )

    def mock_post_request(
        self, mocker, url, fixture_name=None, json=None, status_code=200, **kwargs
    ):
        if not fixture_name:
            mocker.post(url).mock(
                return_value=httpx.Response(status_code, json=json, **kwargs)
            )
        else:
            mocker.post(url).mock(
                return_value=httpx.Response(
                    status_code, json=self.load_json(fixture_name)
                )
            )

    def qs(self, last_request):
        return parse_qs(urlparse(str(last_request.url)).query)
