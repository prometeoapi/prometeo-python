from datetime import datetime


from prometeo.sat.client import (
    SatAPIClient,
    Session,
    BillStatus,
    Motive,
    DocumentType,
    Status,
    SendType,
)
from tests.base_test_case import BaseTestCase
import respx
from six.moves.urllib.parse import parse_qs, urlparse


class TestSession(BaseTestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        client = SatAPIClient("test_api_key", "sandbox")
        self.session_key = "test_session_key"
        self.session = Session(client, "logged_in", self.session_key)

    @respx.mock
    async def test_logout(self):
        self.mock_get_request(respx, "/logout/", "successful_logout")
        await self.session.logout()
        last_request = respx.calls.last.request
        self.assertIn(self.session_key, str(last_request.url))

    @respx.mock
    def test_get_emitted_list(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_list")
        bills = self.session.get_emitted_bills(
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
        )

        self.assertEqual(3, len(bills))
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 4), bills[0].certification_date)
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), bills[0].emitted_date)
        self.assertEqual(BillStatus.VALID.value, bills[0].status)

    @respx.mock
    def test_download_emitted(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_bulk_download")
        downloads = self.session.download_emitted_bills(
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
        )
        last_request = respx.calls.last.request
        qs = parse_qs(urlparse(str(last_request.url)).query)
        self.assertEqual("bulk_download", qs["action"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    @respx.mock
    def test_get_received_list(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_list")
        bills = self.session.get_received_bills(2018, 8, BillStatus.ANY)

        self.assertEqual(3, len(bills))
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 4), bills[0].certification_date)
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), bills[0].emitted_date)
        self.assertEqual(BillStatus.VALID.value, bills[0].status)

    @respx.mock
    def test_download_received(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_bulk_download")
        downloads = self.session.download_received_bills(2018, 5, BillStatus.ANY)
        last_request = respx.calls.last.request
        qs = parse_qs(urlparse(str(last_request.url)).query)
        self.assertEqual("bulk_download", qs["action"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    @respx.mock
    async def test_get_downloads(self):
        self.mock_get_request(respx, "/cfdi/download/", "cfdi_list_downloads")
        downloads = await self.session.get_downloads()

        last_request = respx.calls.last.request
        self.assertIn(self.session_key, str(last_request.url))
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "CAF80916-71AC-4CEA-BECF-F2AC3F394948", downloads[0].request_id
        )

    @respx.mock
    async def test_get_download_from_list(self):
        request_id = "CAF80916-71AC-4CEA-BECF-F2AC3F394948"
        self.mock_get_request(respx, "/cfdi/download/", "cfdi_list_downloads")
        self.mock_get_request(
            respx, "/cfdi/download/{}/".format(request_id), "cfdi_download"
        )
        download_requests = await self.session.get_downloads()
        download = await download_requests[0].get_download()
        self.assertEqual(download.url, "/download/4f3882b1d413f761ced91b6bd583f6ee.zip")

    @respx.mock
    async def test_get_download(self):
        request_id = "50AD2BA1-27AE-4CC3-84FD-265E585A1F67"
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_bulk_download")
        self.mock_get_request(
            respx, "/cfdi/download/{}/".format(request_id), "cfdi_download"
        )

        download_requests = await self.session.download_received_bills(
            2018, 5, BillStatus.ANY
        )
        download = await download_requests[0].get_download()
        self.assertEqual(download.url, "/download/4f3882b1d413f761ced91b6bd583f6ee.zip")

    @respx.mock
    def test_get_acknowledgements(self):
        self.mock_get_request(
            respx, "/ccee/acknowledgment/", "ccee_list_acknowledgements"
        )

        acks = self.session.get_acknowledgements(
            year=2018,
            month_start=1,
            month_end=5,
            motive=Motive.AF,
            document_type=DocumentType.CT,
            status=Status.RECEIVED,
            send_type=SendType.N,
        )
        last_request = respx.calls.last.request
        qs = parse_qs(urlparse(str(last_request.url)).query)
        self.assertEqual(self.session_key, qs["session_key"][0])
        self.assertEqual("2018", qs["year"][0])
        self.assertEqual("1", qs["month_start"][0])
        self.assertEqual("5", qs["month_end"][0])
        self.assertEqual("af", qs["motive"][0])
        self.assertEqual("ct", qs["document_type"][0])
        self.assertEqual("received", qs["status"][0])
        self.assertEqual("n", qs["send_type"][0])
        self.assertEqual(3, len(acks))
        self.assertEqual("0002180100000000325368", acks[0].id)

    @respx.mock
    async def test_download_acknowldegement(self):
        self.mock_get_request(
            respx, "/ccee/acknowledgment/", "ccee_list_acknowledgements"
        )
        self.mock_get_request(
            respx,
            "/ccee/acknowledgment/0002180100000000325368/",
            "ccee_download_acknowledgement",
        )

        acks = await self.session.get_acknowledgements(
            year=2018,
            month_start=1,
            month_end=5,
            motive=Motive.AF,
            document_type=DocumentType.CT,
            status=Status.RECEIVED,
            send_type=SendType.N,
        )
        download = await acks[0].get_download()
        self.assertEqual(download.url, "/download/4f3882b1d413f761ced91b6bd583f6ee.zip")

    @respx.mock
    async def test_download_not_ready(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_bulk_download")
        self.mock_get_request(
            respx,
            "/cfdi/download/50AD2BA1-27AE-4CC3-84FD-265E585A1F67/",
            "not_found",
            status_code=404,
        )

        downloads = await self.session.download_received_bills(2018, 5, BillStatus.ANY)
        self.assertFalse(await downloads[0].is_ready())

    @respx.mock
    async def test_download_ready(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_bulk_download")
        self.mock_get_request(
            respx,
            "/cfdi/download/50AD2BA1-27AE-4CC3-84FD-265E585A1F67/",
            "cfdi_download",
        )

        downloads = await self.session.download_received_bills(2018, 5, BillStatus.ANY)
        self.assertTrue(await downloads[0].is_ready())

    @respx.mock
    def test_restore_session(self):
        self.mock_get_request(respx, "/cfdi/download/", "cfdi_list_downloads")

        session_key = "test_restored_key"
        session = self.client.sat.get_session(session_key)

        session.get_downloads()
        last_request = respx.calls.last.request
        self.assertIn("session_key", str(last_request.url.query))
