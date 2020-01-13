from datetime import datetime
from six.moves.urllib.parse import parse_qs

import requests_mock

from prometeo.sat.client import (
    LoginScope, BillStatus, DownloadAction, Motive, DocumentType, Status, SendType,
)
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestClient(BaseTestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        self.session_key = '123456'

    def test_login_success(self, m):
        self.mock_post_request(m, '/login/', 'successful_login')
        rfc = 'ABC12345DEF'
        password = 'test_password'
        session = self.client.sat.login(
            rfc, password, LoginScope.CFDI
        )
        self.assertEqual('logged_in', session.get_status())
        self.assertEqual(self.session_key, session.get_session_key())

        request_body = parse_qs(m.last_request.text)
        self.assertEqual('sat', request_body['provider'][0])
        self.assertEqual(rfc, request_body['rfc'][0])
        self.assertEqual(password, request_body['password'][0])
        self.assertEqual('cfdi', request_body['scope'][0])

    def test_logout(self, m):
        self.mock_get_request(m, '/logout/', 'successful_logout')
        self.client.sat.logout(self.session_key)
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])

    def test_emitted(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_list')
        self.client.sat.get_emitted(
            self.session_key, datetime(2019, 1, 1), datetime(2019, 5, 1),
            BillStatus.ANY, DownloadAction.LIST,
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('01/01/2019', m.last_request.qs['date_start'][0])
        self.assertEqual('01/05/2019', m.last_request.qs['date_end'][0])
        self.assertEqual('any', m.last_request.qs['status'][0])
        self.assertEqual('list', m.last_request.qs['action'][0])

    def test_get_emitted_list(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_list')
        emitted = self.client.sat.get_emitted(
            self.session_key, datetime(2019, 1, 1), datetime(2019, 5, 1),
            BillStatus.ANY, DownloadAction.LIST,
        )

        self.assertEqual(3, len(emitted))
        self.assertEqual(
            datetime(2018, 8, 29, 20, 50, 4), emitted[0].certification_date
        )
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), emitted[0].emitted_date)
        self.assertEqual(BillStatus.VALID, emitted[0].status)

    def test_get_emitted_bulk_download(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_bulk_download')
        downloads = self.client.sat.get_emitted(
            self.session_key, datetime(2019, 1, 1), datetime(2019, 5, 1),
            BillStatus.ANY, DownloadAction.BULK_DOWNLOAD,
        )

        self.assertEqual('bulk_download', m.last_request.qs['action'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    def test_get_emitted_metadata_download(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_bulk_download')
        downloads = self.client.sat.get_emitted(
            self.session_key, datetime(2019, 1, 1), datetime(2019, 5, 1),
            BillStatus.ANY, DownloadAction.METADATA_DOWNLOAD,
        )

        self.assertEqual('metadata_download', m.last_request.qs['action'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    def test_get_emitted_pdf_export(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_pdf_export')
        downloads = self.client.sat.get_emitted(
            self.session_key, datetime(2019, 1, 1), datetime(2019, 5, 1),
            BillStatus.ANY, DownloadAction.PDF_EXPORT,
        )

        self.assertEqual('pdf_export', m.last_request.qs['action'][0])
        self.assertEqual(1, len(downloads))
        self.assertEqual(
            "/pdf/655ea3b7d0ec5fa1914aca7809e72449.pdf", downloads[0].pdf_url
        )

    def test_download_emitted(self, m):
        bill_id = 'DDAA8B0B-4FDC-43D7-A633-F307B898AB3C'
        self.mock_get_request(
            m, '/cfdi/emitted/{}/'.format(bill_id), 'cfdi_emitted_download'
        )
        download = self.client.sat.download_emitted(self.session_key, bill_id)

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(
            download.download_url, "/download/4f3882b1d413f761ced91b6bd583f6ee.xml"
        )

    def test_get_received(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_list')
        self.client.sat.get_received(
            self.session_key, 2019, 5,
            BillStatus.ANY, DownloadAction.LIST,
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2019', m.last_request.qs['year'][0])
        self.assertEqual('5', m.last_request.qs['month'][0])
        self.assertEqual('any', m.last_request.qs['status'][0])
        self.assertEqual('list', m.last_request.qs['action'][0])

    def test_get_received_list(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_list')
        received = self.client.sat.get_received(
            self.session_key, 2019, 5,
            BillStatus.ANY, DownloadAction.LIST,
        )

        self.assertEqual(3, len(received))
        self.assertEqual(
            datetime(2018, 8, 29, 20, 50, 4), received[0].certification_date
        )
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), received[0].emitted_date)
        self.assertEqual(BillStatus.VALID, received[0].status)

    def test_get_received_bulk_download(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_bulk_download')
        downloads = self.client.sat.get_received(
            self.session_key, 2019, 5,
            BillStatus.ANY, DownloadAction.BULK_DOWNLOAD,
        )

        self.assertEqual('bulk_download', m.last_request.qs['action'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    def test_get_received_metadata_download(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_bulk_download')
        downloads = self.client.sat.get_received(
            self.session_key, 2019, 5,
            BillStatus.ANY, DownloadAction.METADATA_DOWNLOAD,
        )

        self.assertEqual('metadata_download', m.last_request.qs['action'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    def test_get_received_pdf_export(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_pdf_export')
        downloads = self.client.sat.get_received(
            self.session_key, 2019, 5,
            BillStatus.ANY, DownloadAction.PDF_EXPORT,
        )

        self.assertEqual('pdf_export', m.last_request.qs['action'][0])
        self.assertEqual(1, len(downloads))
        self.assertEqual(
            "/pdf/655ea3b7d0ec5fa1914aca7809e72449.pdf", downloads[0].pdf_url
        )

    def test_download_received(self, m):
        bill_id = 'DDAA8B0B-4FDC-43D7-A633-F307B898AB3C'
        self.mock_get_request(
            m, '/cfdi/received/{}/'.format(bill_id), 'cfdi_received_download'
        )
        download = self.client.sat.download_received(self.session_key, bill_id)

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(
            download.download_url, "/download/4f3882b1d413f761ced91b6bd583f6ee.xml"
        )

    def test_get_downloads(self, m):
        self.mock_get_request(m, '/cfdi/download/', 'cfdi_list_downloads')
        downloads = self.client.sat.get_downloads(self.session_key)
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "CAF80916-71AC-4CEA-BECF-F2AC3F394948", downloads[0].request_id
        )

    def test_get_download(self, m):
        request_id = 'DDAA8B0B-4FDC-43D7-A633-F307B898AB3C'
        self.mock_get_request(
            m, '/cfdi/download/{}/'.format(request_id), 'cfdi_download'
        )
        download = self.client.sat.get_download(self.session_key, request_id)
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(
            download.download_url, "/download/4f3882b1d413f761ced91b6bd583f6ee.zip"
        )

    def test_get_acknowledgements(self, m):
        self.mock_get_request(m, '/ccee/acknowledgment/', 'ccee_list_acknowledgements')
        acks = self.client.sat.get_acknowledgements(
            self.session_key, 2018, 1, 5,
            Motive.AF, DocumentType.CT, Status.RECEIVED, SendType.N,
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2018', m.last_request.qs['year'][0])
        self.assertEqual('1', m.last_request.qs['month_start'][0])
        self.assertEqual('5', m.last_request.qs['month_end'][0])
        self.assertEqual('af', m.last_request.qs['motive'][0])
        self.assertEqual('ct', m.last_request.qs['document_type'][0])
        self.assertEqual('received', m.last_request.qs['status'][0])
        self.assertEqual('n', m.last_request.qs['send_type'][0])
        self.assertEqual(3, len(acks))
        self.assertEqual('0002180100000000325368', acks[0].id)

    def test_download_acknowldegement(self, m):
        ack_id = '0002180100000000325368'
        self.mock_get_request(
            m, '/ccee/acknowledgment/{}/'.format(ack_id),
            'ccee_download_acknowledgement'
        )
        download = self.client.sat.download_acknowledgement(self.session_key, ack_id)
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(
            '/download/4f3882b1d413f761ced91b6bd583f6ee.zip', download.download_url
        )
