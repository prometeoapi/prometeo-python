from datetime import datetime
import httpx
import six
from six.moves.urllib.parse import parse_qs
import respx

from prometeo.dian import (
    DocumentType,
    Periodicity,
    QuarterlyPeriod,
    NumerationType,
    MonthlyPeriod,
)
from tests.base_test_case import BaseTestCase


class TestClient(BaseTestCase):
    def setUp(self):
        super(TestClient, self).setUp()
        self.session_key = "123456"
        self.pdf_content = "pdf content"

    async def assert_pdf_downloaded(self, response):
        self.assertEqual(
            six.ensure_binary(self.pdf_content), await response.pdf.get_file()
        )

    def mock_pdf_download(self, mocker, url, fixture_name):
        response_data = self.load_json(fixture_name)
        key = [k for k in response_data.keys() if k != "status"][0]
        mocker.get(url, json=response_data)
        mocker.get(url).mock(
            return_value=httpx.Response(status_code=200, json=response_data)
        )
        mocker.get(response_data[key]["pdf_url"]).mock(
            return_value=httpx.Response(status_code=200, text=self.pdf_content)
        )

    @respx.mock
    async def test_login_company_success(self):
        self.mock_post_request(respx, "/login/", "successful_login")
        session = await self.client.dian.login(
            nit="098765",
            document_type=DocumentType.CEDULA_CIUDADANIA,
            document="12345",
            password="test_password",
        )
        self.assertEqual("logged_in", session.get_status())
        self.assertEqual(self.session_key, session.get_session_key())

        last_request = respx.calls.last.request
        request_body = parse_qs(str(last_request.content.decode("utf-8")))
        self.assertEqual("098765", request_body["nit"][0])
        self.assertEqual("13", request_body["document_type"][0])
        self.assertEqual("12345", request_body["document"][0])
        self.assertEqual("test_password", request_body["password"][0])

    @respx.mock
    async def test_login_person_success(self):
        self.mock_post_request(respx, "/login/", "successful_login")
        session = await self.client.dian.login(
            document_type=DocumentType.CEDULA_CIUDADANIA,
            document="12345",
            password="test_password",
        )
        self.assertEqual("logged_in", session.get_status())
        self.assertEqual("123456", session.get_session_key())

        last_request = respx.calls.last.request
        request_body = parse_qs(str(last_request.content.decode("utf-8")))
        self.assertNotIn("nit", request_body)
        self.assertEqual("13", request_body["document_type"][0])
        self.assertEqual("12345", request_body["document"][0])
        self.assertEqual("test_password", request_body["password"][0])

    @respx.mock
    async def test_get_company_info(self):
        self.mock_get_request(respx, "/company-info/", "company_info")
        info = await self.client.dian.get_company_info(self.session_key)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual(info.reason, "Qualia Fintech SRL")
        self.assertEqual(info.location.country, "Uruguay")
        self.assertEqual(info.accountant.start_date, datetime(2017, 5, 1))

    @respx.mock
    async def test_download_company_info(self):
        self.mock_pdf_download(respx, "/company-info/", "company_info")
        info = await self.client.dian.get_company_info(self.session_key)
        await self.assert_pdf_downloaded(info)

    @respx.mock
    async def test_get_balances(self):
        self.mock_get_request(respx, "/balances/", "company_balances")
        balances = await self.client.dian.get_balances(self.session_key)
        last_request = respx.calls.last.request
        self.assertEqual(2, len(balances))
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])

    @respx.mock
    async def test_get_rent_declaration(self):
        self.mock_get_request(respx, "/rent/", "company_rent")
        rent = await self.client.dian.get_rent_declaration(self.session_key, 2019)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2019", self.qs(last_request)["year"][0])
        self.assertEqual(rent.nit, "333222251")
        self.assertEqual(6, len(rent.fields))

    @respx.mock
    async def test_download_rent_declaration(self):
        self.mock_pdf_download(respx, "/rent/", "company_rent")
        rent = await self.client.dian.get_rent_declaration(self.session_key, 2019)
        await self.assert_pdf_downloaded(rent)

    @respx.mock
    async def test_get_vat_declaration(self):
        self.mock_get_request(respx, "/vat/", "vat_declaration")
        vat = await self.client.dian.get_vat_declaration(
            self.session_key,
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
    async def test_download_vat_declaration(self):
        self.mock_pdf_download(respx, "/vat/", "vat_declaration")
        vat = await self.client.dian.get_vat_declaration(
            self.session_key,
            2019,
            Periodicity.QUARTERLY,
            QuarterlyPeriod.JANUARY_APRIL,
        )
        await self.assert_pdf_downloaded(vat)

    @respx.mock
    async def test_get_numeration(self):
        self.mock_get_request(respx, "/numeration/", "numeration_authorization")
        numerations = await self.client.dian.get_numeration(
            self.session_key,
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
    async def test_get_numeration_no_pdf(self):
        self.mock_get_request(respx, "/numeration/", "numeration_no_pdf")
        numerations = await self.client.dian.get_numeration(
            self.session_key,
            NumerationType.Authorization,
            datetime(2019, 1, 1),
            datetime(2019, 5, 1),
        )

        self.assertEqual(1, len(numerations))
        self.assertEqual(None, numerations[0].department)

    @respx.mock
    async def test_retentions(self):
        self.mock_get_request(respx, "/retentions/", "retentions")
        retentions = await self.client.dian.get_retentions(
            self.session_key, "2018", MonthlyPeriod.NOVEMBER
        )

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, self.qs(last_request)["session_key"][0])
        self.assertEqual("2018", self.qs(last_request)["year"][0])
        self.assertEqual("11", self.qs(last_request)["period"][0])

        self.assertEqual("Qualia Fintech SRL", retentions.reason)

    @respx.mock
    async def test_download_retentions(self):
        self.mock_pdf_download(respx, "/retentions/", "retentions")
        retentions = await self.client.dian.get_retentions(
            self.session_key, "2018", MonthlyPeriod.NOVEMBER
        )
        await self.assert_pdf_downloaded(retentions)
