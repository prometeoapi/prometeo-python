import json
import unittest

from prometeo import Client


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client("test_key")

    @property
    def module_name(self):
        return self.__class__.__module__.split(".")[1]

    def load_json(self, file_name):
        with open(f"tests/fixtures/{self.module_name}/{file_name}.json") as f:
            return json.load(f)

    def mock_get_request(self, mocker, url, fixture_name, status_code=200):
        mocker.get(url, status_code=status_code, json=self.load_json(fixture_name))

    def mock_post_request(self, mocker, url, fixture_name, status_code=200):
        mocker.post(url, status_code=status_code, json=self.load_json(fixture_name))
