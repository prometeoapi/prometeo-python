from datetime import datetime
from six.moves.urllib.parse import parse_qs


from prometeo.sat.client import (
    LoginScope,
    BillStatus,
    DownloadAction,
    Motive,
    DocumentType,
    Status,
    SendType,
)
from tests.base_test_case import BaseTestCase
import respx


class TestClient(BaseTestCase):
    def setUp(self):
        super(TestClient, self).setUp()
        self.session_key = "123456"

    @respx.mock
    async def test_login_success(self):
        self.mock_post_request(respx, "/login/", "successful_login")
        rfc = "ABC12345DEF"
        password = "test_password"
        session = await self.client.sat.login(rfc, password, LoginScope.CFDI)
        self.assertEqual("logged_in", session.get_status())
        self.assertEqual(self.session_key, session.get_session_key())

        last_request = respx.calls.last.request
        request_body = parse_qs(str(last_request.content.decode("utf-8")))
        self.assertEqual("sat", request_body["provider"][0])
        self.assertEqual(rfc, request_body["rfc"][0])
        self.assertEqual(password, request_body["password"][0])
        self.assertEqual("cfdi", request_body["scope"][0])

    @respx.mock
    async def test_logout(self):
        self.mock_get_request(respx, "/logout/", "successful_logout")
        await self.client.sat.logout(self.session_key)
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])

    @respx.mock
    async def test_emitted(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_list")
        await self.client.sat.get_emitted(
            self.session_key,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
            DownloadAction.LIST,
        )

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("01/01/2019", self.qs(last_request)["date_start"][0])
        self.assertEqual("01/05/2019", self.qs(last_request)["date_end"][0])
        self.assertEqual("any", self.qs(last_request)["status"][0])
        self.assertEqual("list", self.qs(last_request)["action"][0])

    @respx.mock
    async def test_get_emitted_list(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_list")
        emitted = await self.client.sat.get_emitted(
            self.session_key,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
            DownloadAction.LIST,
        )

        self.assertEqual(3, len(emitted))
        self.assertEqual(
            datetime(2018, 8, 29, 20, 50, 4), emitted[0].certification_date
        )
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), emitted[0].emitted_date)
        self.assertEqual(BillStatus.VALID.value, emitted[0].status)

    @respx.mock
    async def test_get_emitted_bulk_download(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_bulk_download")
        downloads = await self.client.sat.get_emitted(
            self.session_key,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
            DownloadAction.BULK_DOWNLOAD,
        )
        last_request = respx.calls.last.request
        self.assertEqual("bulk_download", self.qs(last_request)["action"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    @respx.mock
    async def test_get_emitted_metadata_download(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_bulk_download")
        downloads = await self.client.sat.get_emitted(
            self.session_key,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
            DownloadAction.METADATA_DOWNLOAD,
        )

        last_request = respx.calls.last.request
        self.assertEqual("metadata_download", self.qs(last_request)["action"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    @respx.mock
    async def test_get_emitted_pdf_export(self):
        self.mock_get_request(respx, "/cfdi/emitted/", "cfdi_emitted_pdf_export")
        downloads = await self.client.sat.get_emitted(
            self.session_key,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
            BillStatus.ANY,
            DownloadAction.PDF_EXPORT,
        )

        last_request = respx.calls.last.request
        self.assertEqual("pdf_export", self.qs(last_request)["action"][0])
        self.assertEqual(1, len(downloads))
        self.assertEqual(
            "/pdf/655ea3b7d0ec5fa1914aca7809e72449.pdf", downloads[0].pdf_url
        )

    @respx.mock
    async def test_download_emitted(self):
        bill_id = "DDAA8B0B-4FDC-43D7-A633-F307B898AB3C"
        self.mock_get_request(
            respx, "/cfdi/emitted/{}/".format(bill_id), "cfdi_emitted_download"
        )
        download = await self.client.sat.download_emitted(self.session_key, bill_id)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(
            download.download_url, "/download/4f3882b1d413f761ced91b6bd583f6ee.xml"
        )

    @respx.mock
    async def test_get_received(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_list")
        await self.client.sat.get_received(
            self.session_key,
            2019,
            5,
            BillStatus.ANY,
            DownloadAction.LIST,
        )

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2019", self.qs(last_request)["year"][0])
        self.assertEqual("5", self.qs(last_request)["month"][0])
        self.assertEqual("any", self.qs(last_request)["status"][0])
        self.assertEqual("list", self.qs(last_request)["action"][0])

    @respx.mock
    async def test_get_received_list(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_list")
        received = await self.client.sat.get_received(
            self.session_key,
            2019,
            5,
            BillStatus.ANY,
            DownloadAction.LIST,
        )

        self.assertEqual(3, len(received))
        self.assertEqual(
            datetime(2018, 8, 29, 20, 50, 4), received[0].certification_date
        )
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), received[0].emitted_date)
        self.assertEqual(BillStatus.VALID.value, received[0].status)

    @respx.mock
    async def test_get_received_bulk_download(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_bulk_download")
        downloads = await self.client.sat.get_received(
            self.session_key,
            2019,
            5,
            BillStatus.ANY,
            DownloadAction.BULK_DOWNLOAD,
        )
        last_request = respx.calls.last.request
        self.assertEqual("bulk_download", self.qs(last_request)["action"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    @respx.mock
    async def test_get_received_metadata_download(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_bulk_download")
        downloads = await self.client.sat.get_received(
            self.session_key,
            2019,
            5,
            BillStatus.ANY,
            DownloadAction.METADATA_DOWNLOAD,
        )

        last_request = respx.calls.last.request
        self.assertEqual("metadata_download", self.qs(last_request)["action"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    @respx.mock
    async def test_get_received_pdf_export(self):
        self.mock_get_request(respx, "/cfdi/received/", "cfdi_received_pdf_export")
        downloads = await self.client.sat.get_received(
            self.session_key,
            2019,
            5,
            BillStatus.ANY,
            DownloadAction.PDF_EXPORT,
        )
        last_request = respx.calls.last.request
        self.assertEqual("pdf_export", self.qs(last_request)["action"][0])
        self.assertEqual(1, len(downloads))
        self.assertEqual(
            "/pdf/655ea3b7d0ec5fa1914aca7809e72449.pdf", downloads[0].pdf_url
        )

    @respx.mock
    async def test_download_received(self):
        bill_id = "DDAA8B0B-4FDC-43D7-A633-F307B898AB3C"
        self.mock_get_request(
            respx, "/cfdi/received/{}/".format(bill_id), "cfdi_received_download"
        )
        download = await self.client.sat.download_received(self.session_key, bill_id)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(
            download.download_url, "/download/4f3882b1d413f761ced91b6bd583f6ee.xml"
        )

    @respx.mock
    async def test_get_downloads(self):
        self.mock_get_request(respx, "/cfdi/download/", "cfdi_list_downloads")
        downloads = await self.client.sat.get_downloads(self.session_key)
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "CAF80916-71AC-4CEA-BECF-F2AC3F394948", downloads[0].request_id
        )

    @respx.mock
    async def test_get_download(self):
        request_id = "DDAA8B0B-4FDC-43D7-A633-F307B898AB3C"
        self.mock_get_request(
            respx, "/cfdi/download/{}/".format(request_id), "cfdi_download"
        )
        download = await self.client.sat.get_download(self.session_key, request_id)
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(
            download.download_url, "/download/4f3882b1d413f761ced91b6bd583f6ee.zip"
        )

    @respx.mock
    async def test_get_acknowledgements(self):
        self.mock_get_request(
            respx, "/ccee/acknowledgment/", "ccee_list_acknowledgements"
        )
        acks = await self.client.sat.get_acknowledgements(
            self.session_key,
            2018,
            1,
            5,
            Motive.AF,
            DocumentType.CT,
            Status.RECEIVED,
            SendType.N,
        )

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2018", self.qs(last_request)["year"][0])
        self.assertEqual("1", self.qs(last_request)["month_start"][0])
        self.assertEqual("5", self.qs(last_request)["month_end"][0])
        self.assertEqual("af", self.qs(last_request)["motive"][0])
        self.assertEqual("ct", self.qs(last_request)["document_type"][0])
        self.assertEqual("received", self.qs(last_request)["status"][0])
        self.assertEqual("n", self.qs(last_request)["send_type"][0])
        self.assertEqual(3, len(acks))
        self.assertEqual("0002180100000000325368", acks[0].id)

    @respx.mock
    async def test_download_acknowldegement(self):
        ack_id = "0002180100000000325368"
        self.mock_get_request(
            respx,
            "/ccee/acknowledgment/{}/".format(ack_id),
            "ccee_download_acknowledgement",
        )
        download = await self.client.sat.download_acknowledgement(
            self.session_key, ack_id
        )
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(
            "/download/4f3882b1d413f761ced91b6bd583f6ee.zip", download.download_url
        )
