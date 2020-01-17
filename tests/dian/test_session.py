from datetime import datetime

from prometeo.dian.client import (
    DianAPIClient, Session, Periodicity, QuarterlyPeriod, NumerationType, MonthlyPeriod
)
from tests.base_test_case import BaseTestCase

import requests_mock


@requests_mock.Mocker()
class TestSession(BaseTestCase):

    def setUp(self):
        super(TestSession, self).setUp()
        client = DianAPIClient('test_api_key', 'testing')
        self.session_key = 'test_session_key'
        self.session = Session(client, 'logged_in', self.session_key)

    def test_get_company_info(self, m):
        self.mock_get_request(m, '/company-info/', 'company_info')
        info = self.session.get_company_info()

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual(info.reason, "Qualia Fintech SRL")
        self.assertEqual(info.location.country, "Uruguay")
        self.assertEqual(info.accountant.start_date, datetime(2017, 5, 1))

    def test_get_balances(self, m):
        self.mock_get_request(m, '/balances/', 'company_balances')
        balances = self.session.get_balances()
        self.assertEqual(2, len(balances))
        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])

    def test_get_rent_declaration(self, m):
        self.mock_get_request(m, '/rent/', 'company_rent')
        rent = self.session.get_rent_declaration(2019)

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2019', m.last_request.qs['year'][0])
        self.assertEqual(rent.nit, "333222251")
        self.assertEqual(6, len(rent.fields))

    def test_get_vat_declaration(self, m):
        self.mock_get_request(m, '/vat/', 'vat_declaration')
        vat = self.session.get_vat_declaration(
            2019, Periodicity.QUARTERLY, QuarterlyPeriod.JANUARY_APRIL,
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2019', m.last_request.qs['year'][0])
        self.assertEqual('q', m.last_request.qs['periodicity'][0])
        self.assertEqual('1', m.last_request.qs['period'][0])
        self.assertEqual(vat.nit, "123332211")
        self.assertEqual(6, len(vat.fields))

    def test_get_numeration(self, m):
        self.mock_get_request(m, '/numeration/', 'numeration_authorization')
        numerations = self.session.get_numeration(
            NumerationType.Authorization, datetime(2019, 1, 1), datetime(2019, 5, 1),
        )

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('authorization', m.last_request.qs['type'][0])
        self.assertEqual('01/01/2019', m.last_request.qs['date_start'][0])
        self.assertEqual('01/05/2019', m.last_request.qs['date_end'][0])

        self.assertEqual(1, len(numerations))
        self.assertEqual("Antioquia", numerations[0].department)

    def test_retentions(self, m):
        self.mock_get_request(m, '/retentions/', 'retentions')
        retentions = self.session.get_retentions(2018, MonthlyPeriod.NOVEMBER)

        self.assertEqual(self.session_key, m.last_request.qs['session_key'][0])
        self.assertEqual('2018', m.last_request.qs['year'][0])
        self.assertEqual('11', m.last_request.qs['period'][0])

        self.assertEqual("Qualia Fintech SRL", retentions.reason)

    def test_restore_session(self, m):
        self.mock_get_request(m, '/balances/', 'company_balances')

        session_key = 'test_restored_key'
        session = self.client.dian.get_session(session_key)

        session.get_balances()
        self.assertEqual(session_key, m.last_request.qs['session_key'][0])
