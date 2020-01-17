from datetime import datetime

import requests_mock

from prometeo.sat.client import (
    SatAPIClient, Session, BillStatus, Motive, DocumentType, Status, SendType,
)
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestSession(BaseTestCase):

    def setUp(self):
        super(TestSession, self).setUp()
        client = SatAPIClient('test_api_key', 'testing')
        self.session_key = 'test_session_key'
        self.session = Session(client, 'logged_in', self.session_key)

    def test_logout(self, m):
        self.mock_get_request(m, '/logout/', 'successful_logout')
        self.session.logout()
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])

    def test_get_emitted_list(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_list')
        bills = self.session.get_emitted_bills(
            datetime(2019, 1, 1), datetime(2019, 5, 1), BillStatus.ANY,
        )

        self.assertEqual(3, len(bills))
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 4), bills[0].certification_date)
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), bills[0].emitted_date)
        self.assertEqual(BillStatus.VALID, bills[0].status)

    def test_download_emitted(self, m):
        self.mock_get_request(m, '/cfdi/emitted/', 'cfdi_emitted_bulk_download')
        downloads = self.session.download_emitted_bills(
            datetime(2019, 1, 1), datetime(2019, 5, 1), BillStatus.ANY,
        )
        self.assertEqual('bulk_download', m.last_request.qs['action'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    def test_get_received_list(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_list')
        bills = self.session.get_received_bills(2018, 8, BillStatus.ANY)

        self.assertEqual(3, len(bills))
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 4), bills[0].certification_date)
        self.assertEqual(datetime(2018, 8, 29, 20, 50, 3), bills[0].emitted_date)
        self.assertEqual(BillStatus.VALID, bills[0].status)

    def test_download_received(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_bulk_download')
        downloads = self.session.download_received_bills(
            2018, 5, BillStatus.ANY
        )
        self.assertEqual('bulk_download', m.last_request.qs['action'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "50AD2BA1-27AE-4CC3-84FD-265E585A1F67", downloads[0].request_id
        )

    def test_get_downloads(self, m):
        self.mock_get_request(m, '/cfdi/download/', 'cfdi_list_downloads')
        downloads = self.session.get_downloads()
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(2, len(downloads))
        self.assertEqual(
            "CAF80916-71AC-4CEA-BECF-F2AC3F394948", downloads[0].request_id
        )

    def test_get_download_from_list(self, m):
        request_id = 'CAF80916-71AC-4CEA-BECF-F2AC3F394948'
        self.mock_get_request(m, '/cfdi/download/', 'cfdi_list_downloads')
        self.mock_get_request(
            m, '/cfdi/download/{}/'.format(request_id), 'cfdi_download'
        )
        download_requests = self.session.get_downloads()
        download = download_requests[0].get_download()
        self.assertEqual(download.url, '/download/4f3882b1d413f761ced91b6bd583f6ee.zip')

    def test_get_download(self, m):
        request_id = '50AD2BA1-27AE-4CC3-84FD-265E585A1F67'
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_bulk_download')
        self.mock_get_request(
            m, '/cfdi/download/{}/'.format(request_id), 'cfdi_download'
        )

        download_requests = self.session.download_received_bills(
            2018, 5, BillStatus.ANY
        )
        download = download_requests[0].get_download()
        self.assertEqual(download.url, '/download/4f3882b1d413f761ced91b6bd583f6ee.zip')

    def test_get_acknowledgements(self, m):
        self.mock_get_request(m, '/ccee/acknowledgment/', 'ccee_list_acknowledgements')

        acks = self.session.get_acknowledgements(
            year=2018,
            month_start=1,
            month_end=5,
            motive=Motive.AF,
            document_type=DocumentType.CT,
            status=Status.RECEIVED,
            send_type=SendType.N,
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
        self.mock_get_request(m, '/ccee/acknowledgment/', 'ccee_list_acknowledgements')
        self.mock_get_request(
            m, '/ccee/acknowledgment/0002180100000000325368/',
            'ccee_download_acknowledgement'
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
        download = acks[0].get_download()
        self.assertEqual(download.url, "/download/4f3882b1d413f761ced91b6bd583f6ee.zip")

    def test_download_not_ready(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_bulk_download')
        self.mock_get_request(
            m,
            '/cfdi/download/50AD2BA1-27AE-4CC3-84FD-265E585A1F67/',
            'not_found',
            status_code=404
        )

        downloads = self.session.download_received_bills(
            2018, 5, BillStatus.ANY
        )
        self.assertFalse(downloads[0].is_ready())

    def test_download_ready(self, m):
        self.mock_get_request(m, '/cfdi/received/', 'cfdi_received_bulk_download')
        self.mock_get_request(
            m,
            '/cfdi/download/50AD2BA1-27AE-4CC3-84FD-265E585A1F67/',
            'cfdi_download',
        )

        downloads = self.session.download_received_bills(
            2018, 5, BillStatus.ANY
        )
        self.assertTrue(downloads[0].is_ready())

    def test_restore_session(self, m):
        self.mock_get_request(m, '/cfdi/download/', 'cfdi_list_downloads')

        session_key = 'test_restored_key'
        session = self.client.sat.get_session(session_key)

        session.get_downloads()
        self.assertEqual(session_key, m.last_request.qs['session_key'][0])
