from datetime import datetime

import six
from six.moves.urllib.parse import parse_qs
import requests_mock

from prometeo.dian import (
    DocumentType, Periodicity, QuarterlyPeriod, NumerationType, MonthlyPeriod,
)
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestClient(BaseTestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        self.session_key = '123456'
        self.pdf_content = 'pdf content'

    def assert_pdf_downloaded(self, response):
        self.assertEqual(six.ensure_binary(self.pdf_content), response.pdf.get_file())

    def mock_pdf_download(self, mocker, url, fixture_name):
        response_data = self.load_json(fixture_name)
        key = [k for k in response_data.keys() if k != 'status'][0]
        mocker.get(url, json=response_data)
        mocker.get(response_data[key]['pdf_url'], text=self.pdf_content)

    def test_login_company_success(self, m):
        self.mock_post_request(m, '/login/', 'successful_login')
        session = self.client.dian.login(
            nit='098765',
            document_type=DocumentType.CEDULA_CIUDADANIA,
            document='12345',
            password='test_password',
        )
        self.assertEqual('logged_in', session.get_status())
        self.assertEqual(self.session_key, session.get_session_key())

        request_body = parse_qs(m.last_request.text)
        self.assertEqual('098765', request_body['nit'][0])
        self.assertEqual('13', request_body['document_type'][0])
        self.assertEqual('12345', request_body['document'][0])
        self.assertEqual('test_password', request_body['password'][0])

    def test_login_person_success(self, m):
        self.mock_post_request(m, '/login/', 'successful_login')
        session = self.client.dian.login(
            document_type=DocumentType.CEDULA_CIUDADANIA,
            document='12345',
            password='test_password',
        )
        self.assertEqual('logged_in', session.get_status())
        self.assertEqual('123456', session.get_session_key())

        request_body = parse_qs(m.last_request.text)
        self.assertNotIn('nit', request_body)
        self.assertEqual('13', request_body['document_type'][0])
        self.assertEqual('12345', request_body['document'][0])
        self.assertEqual('test_password', request_body['password'][0])

    def test_get_company_info(self, m):
        self.mock_get_request(m, '/company-info/', 'company_info')
        info = self.client.dian.get_company_info(self.session_key)

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(info.reason, "Qualia Fintech SRL")
        self.assertEqual(info.location.country, "Uruguay")
        self.assertEqual(info.accountant.start_date, datetime(2017, 5, 1))

    def test_download_company_info(self, m):
        self.mock_pdf_download(m, '/company-info/', 'company_info')
        info = self.client.dian.get_company_info(self.session_key)
        self.assert_pdf_downloaded(info)

    def test_get_balances(self, m):
        self.mock_get_request(m, '/balances/', 'company_balances')
        balances = self.client.dian.get_balances(self.session_key)
        self.assertEqual(2, len(balances))
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])

    def test_get_rent_declaration(self, m):
        self.mock_get_request(m, '/rent/', 'company_rent')
        rent = self.client.dian.get_rent_declaration(self.session_key, 2019)

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2019', m.last_request.qs['year'][0])
        self.assertEqual(rent.nit, "333222251")
        self.assertEqual(6, len(rent.fields))

    def test_download_rent_declaration(self, m):
        self.mock_pdf_download(m, '/rent/', 'company_rent')
        rent = self.client.dian.get_rent_declaration(self.session_key, 2019)
        self.assert_pdf_downloaded(rent)

    def test_get_vat_declaration(self, m):
        self.mock_get_request(m, '/vat/', 'vat_declaration')
        vat = self.client.dian.get_vat_declaration(
            self.session_key,
            2019,
            Periodicity.QUARTERLY,
            QuarterlyPeriod.JANUARY_APRIL,
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2019', m.last_request.qs['year'][0])
        self.assertEqual('q', m.last_request.qs['periodicity'][0])
        self.assertEqual('1', m.last_request.qs['period'][0])
        self.assertEqual(vat.nit, "123332211")
        self.assertEqual(6, len(vat.fields))

    def test_download_vat_declaration(self, m):
        self.mock_pdf_download(m, '/vat/', 'vat_declaration')
        vat = self.client.dian.get_vat_declaration(
            self.session_key,
            2019,
            Periodicity.QUARTERLY,
            QuarterlyPeriod.JANUARY_APRIL,
        )
        self.assert_pdf_downloaded(vat)

    def test_get_numeration(self, m):
        self.mock_get_request(m, '/numeration/', 'numeration_authorization')
        numerations = self.client.dian.get_numeration(
            self.session_key, NumerationType.Authorization,
            datetime(2019, 1, 1), datetime(2019, 5, 1),
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('authorization', m.last_request.qs['type'][0])
        self.assertEqual('01/01/2019', m.last_request.qs['date_start'][0])
        self.assertEqual('01/05/2019', m.last_request.qs['date_end'][0])

        self.assertEqual(1, len(numerations))
        self.assertEqual("Antioquia", numerations[0].department)

    def test_get_numeration_no_pdf(self, m):
        self.mock_get_request(m, '/numeration/', 'numeration_no_pdf')
        numerations = self.client.dian.get_numeration(
            self.session_key, NumerationType.Authorization,
            datetime(2019, 1, 1), datetime(2019, 5, 1),
        )

        self.assertEqual(1, len(numerations))
        self.assertEqual(None, numerations[0].department)

    def test_retentions(self, m):
        self.mock_get_request(m, '/retentions/', 'retentions')
        retentions = self.client.dian.get_retentions(
            self.session_key, '2018', MonthlyPeriod.NOVEMBER
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2018', m.last_request.qs['year'][0])
        self.assertEqual('11', m.last_request.qs['period'][0])

        self.assertEqual("Qualia Fintech SRL", retentions.reason)

    def test_download_retentions(self, m):
        self.mock_pdf_download(m, '/retentions/', 'retentions')
        retentions = self.client.dian.get_retentions(
            self.session_key, '2018', MonthlyPeriod.NOVEMBER
        )
        self.assert_pdf_downloaded(retentions)
