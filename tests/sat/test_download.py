import requests_mock

from prometeo.sat.client import SatAPIClient
from prometeo.base_client import Download
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestSession(BaseTestCase):

    def setUp(self):
        super(TestSession, self).setUp()
        self.client = SatAPIClient('test_api_key', 'testing')

    def test_download_file(self, m):
        file_url = '/download/file.txt'
        file_content = 'content'
        m.get(file_url, text=file_content)
        download = Download(self.client, file_url)
        self.assertEqual(download.get_file().decode(), file_content)
