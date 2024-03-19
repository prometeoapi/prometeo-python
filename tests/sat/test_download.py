from prometeo.sat.client import SatAPIClient
from prometeo.base_client import Download
from tests.base_test_case import BaseTestCase
import respx


class TestSession(BaseTestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        self.client = SatAPIClient("test_api_key", "sandbox")

    @respx.mock
    async def test_download_file(self):
        file_url = "/download/file.txt"
        file_content = "content"
        self.mock_get_request(respx, file_url, text=file_content)
        download = Download(self.client, file_url)
        file = await download.get_file()
        self.assertEqual(file.decode(), file_content)
