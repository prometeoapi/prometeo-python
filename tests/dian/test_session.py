from datetime import datetime

from prometeo.dian.client import (
    DianAPIClient,
    Session,
    Periodicity,
    QuarterlyPeriod,
    NumerationType,
    MonthlyPeriod,
)
from tests.base_test_case import BaseTestCase
import respx


class TestSession(BaseTestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        client = DianAPIClient("test_api_key", "sandbox")
        self.session_key = "test_session_key"
        self.session = Session(client, "logged_in", self.session_key)

    @respx.mock
    def test_get_company_info(self):
        self.mock_get_request(respx, "/company-info/", "company_info")
        info = self.session.get_company_info()

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(info.reason, "Qualia Fintech SRL")
        self.assertEqual(info.location.country, "Uruguay")
        self.assertEqual(info.accountant.start_date, datetime(2017, 5, 1))

    @respx.mock
    def test_get_balances(self):
        self.mock_get_request(respx, "/balances/", "company_balances")
        balances = self.session.get_balances()
        last_request = respx.calls.last.request
        self.assertEqual(2, len(balances))
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])

    @respx.mock
    def test_get_rent_declaration(self):
        self.mock_get_request(respx, "/rent/", "company_rent")
        rent = self.session.get_rent_declaration(2019)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2019", self.qs(last_request)["year"][0])
        self.assertEqual(rent.nit, "333222251")
        self.assertEqual(6, len(rent.fields))

    @respx.mock
    def test_get_vat_declaration(self):
        self.mock_get_request(respx, "/vat/", "vat_declaration")
        vat = self.session.get_vat_declaration(
            2019,
            Periodicity.QUARTERLY,
            QuarterlyPeriod.JANUARY_APRIL,
        )

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2019", self.qs(last_request)["year"][0])
        self.assertEqual("q", self.qs(last_request)["periodicity"][0])
        self.assertEqual("1", self.qs(last_request)["period"][0])
        self.assertEqual(vat.nit, "123332211")
        self.assertEqual(6, len(vat.fields))

    @respx.mock
    def test_get_numeration(self):
        self.mock_get_request(respx, "/numeration/", "numeration_authorization")
        numerations = self.session.get_numeration(
            NumerationType.Authorization,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
        )

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("authorization", self.qs(last_request)["type"][0])
        self.assertEqual("01/01/2019", self.qs(last_request)["date_start"][0])
        self.assertEqual("01/05/2019", self.qs(last_request)["date_end"][0])

        self.assertEqual(1, len(numerations))
        self.assertEqual("Antioquia", numerations[0].department)

    @respx.mock
    def test_retentions(self):
        self.mock_get_request(respx, "/retentions/", "retentions")
        retentions = self.session.get_retentions(2018, MonthlyPeriod.NOVEMBER)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2018", self.qs(last_request)["year"][0])
        self.assertEqual("11", self.qs(last_request)["period"][0])

        self.assertEqual("Qualia Fintech SRL", retentions.reason)

    @respx.mock
    def test_restore_session(self):
        self.mock_get_request(respx, "/balances/", "company_balances")

        session_key = "test_restored_key"
        session = self.client.dian.get_session(session_key)

        session.get_balances()

        last_request = respx.calls.last.request
        self.assertEqual(session_key, self.qs(last_request)["session_key"][0])
