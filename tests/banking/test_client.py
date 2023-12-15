from datetime import datetime

from six.moves.urllib.parse import parse_qs, urlparse


from prometeo import exceptions
from prometeo.banking import exceptions as banking_exceptions
from prometeo.banking.client import Account, CreditCard
from prometeo.banking.models import Account as AccountModel
from prometeo.banking.models import CreditCard as CreditCardModel
from tests.base_test_case import BaseTestCase
import respx


class TestClient(BaseTestCase):
    @respx.mock
    def test_login_success(self):
        self.mock_post_request(
            respx,
            "/login/",
            json={
                "status": "logged_in",
                "key": "123456",
            },
        )
        session = self.client.banking.new_session()
        session.login(
            provider="test_provider",
            username="test_username",
            password="test_password",
        )
        self.assertEqual("logged_in", session.get_status())
        self.assertEqual("123456", session.get_session_key())

    @respx.mock
    def test_login_wrong_credentials(self):
        self.mock_post_request(
            respx,
            "/login/",
            status_code=403,
            json={
                "status": "wrong_credentials",
                "message": "wrong credentials",
            },
        )
        with self.assertRaises(exceptions.WrongCredentialsError):
            session = self.client.banking.new_session()
            session.login(
                provider="test_provider",
                username="test_username",
                password="test_password",
            )

    @respx.mock
    def test_generic_login_error(self):
        self.mock_post_request(
            respx,
            "/login/",
            status_code=200,
            json={
                "status": "error",
                "message": "An error has ocurred.",
            },
        )
        with self.assertRaises(banking_exceptions.BankingClientError):
            session = self.client.banking.new_session()
            session.login(
                provider="test_provider",
                username="test_username",
                password="test_password",
            )

    @respx.mock
    def test_login_select_client(self):
        self.mock_post_request(
            respx,
            "/login/",
            json={
                "status": "select_client",
                "key": "123456",
            },
        )
        self.mock_get_request(
            respx,
            "/client/",
            json={
                "status": "success",
                "clients": {"0": "First Client", "1": "Second Client"},
            },
        )
        self.mock_get_request(respx, "/client/1/", json={"status": "success"})
        session = self.client.banking.new_session()
        session.login(
            provider="test_provider",
            username="test_username",
            password="test_password",
        )
        self.assertEqual("select_client", session.get_status())
        self.assertEqual("123456", session.get_session_key())

        clients = session.get_clients()
        history = respx.calls
        self.assertEqual("/client/", history[-1].request.url.path)

        client = [client for client in clients if client.id == "1"][0]
        session.select_client(client)
        self.assertEqual("/client/1/", history[-1].request.url.path)

    @respx.mock
    def test_login_interactive(self):
        session_key = "123456"
        personal_question = "¿Cuántos baños tenia la casa de mis padres?"
        self.mock_post_request(
            respx,
            "/login/",
            json={
                "status": "interaction_required",
                "context": personal_question,
                "field": "personal_question",
                "key": session_key,
            },
        )
        session = self.client.banking.new_session()
        session.login(
            provider="test_provider",
            username="test_username",
            password="test_password",
        )
        self.assertEqual("interaction_required", session.get_status())
        self.assertEqual(session_key, session.get_session_key())
        self.assertEqual(personal_question, session.get_interactive_context())

        self.mock_post_request(
            respx,
            "/login/",
            json={
                "status": "logged_in",
            },
        )
        challenge_answer = "test answer"
        session.finish_login(
            "test_provider", "test_username", "test_password", challenge_answer
        )
        last_request = respx.calls.last.request
        request_body = parse_qs(str(last_request.content))
        self.assertIn(
            challenge_answer,
            request_body["personal_question"][0],
        )
        self.assertEqual(last_request.headers["X-Session-Key"], session_key)

    @respx.mock
    def test_get_accounts(self):
        self.mock_get_request(
            respx,
            "/account/",
            json={
                "accounts": [
                    {
                        "balance": 1234.95,
                        "branch": "02 - 18 De Julio",
                        "currency": "UYU",
                        "id": "hash1",
                        "name": "Cuenta total",
                        "number": "001234567890",
                    },
                    {
                        "balance": 53.96,
                        "branch": "61 - Ciudad Vieja",
                        "currency": "USD",
                        "id": "hash4",
                        "name": "Caja De Ahorro Atm",
                        "number": "004327567890",
                    },
                ],
                "status": "success",
            },
        )
        session_key = "test_session_key"
        session = self.client.banking.get_session(session_key)
        accounts = session.get_accounts()
        last_request = respx.calls.last.request
        self.assertEqual("/account/", str(last_request.url.path))
        self.assertEqual(session_key, last_request.headers["X-Session-Key"])
        self.assertEqual(2, len(accounts))
        self.assertEqual("Cuenta total", accounts[0].name)
        self.assertEqual("Caja De Ahorro Atm", accounts[1].name)

    @respx.mock
    def test_get_movements(self):
        self.mock_get_request(
            respx,
            "/movement/",
            json={
                "movements": [
                    {
                        "credit": "",
                        "date": "12/01/2019",
                        "debit": 3500,
                        "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.C. ",
                        "id": "-890185180",
                        "reference": "000000005084",
                        "extra_data": None,
                    },
                    {
                        "credit": "",
                        "date": "05/07/2019",
                        "debit": 16000,
                        "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.H Y ",
                        "id": 1024917397,
                        "reference": "000000002931",
                        "extra_data": None,
                    },
                ],
                "status": "success",
            },
        )
        session_key = "test_session_key"
        account_number = "001234567"
        currency_code = "USD"
        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        account = Account(
            self.client.banking,
            session_key,
            AccountModel(
                id="12345",
                name="Cuenta total",
                number="001234567",
                branch="02 - 18 De Julio",
                currency="USD",
                balance=1234.95,
            ),
        )
        movements = account.get_movements(date_start, date_end)
        last_request = respx.calls.last.request
        qs = parse_qs(urlparse(str(last_request.url)).query)
        self.assertEqual("/movement/", last_request.url.path)
        self.assertEqual(session_key, last_request.headers["X-Session-Key"])
        self.assertEqual(account_number, qs["account"][0])
        self.assertEqual(currency_code, qs["currency"][0])
        self.assertEqual("01/01/2019", qs["date_start"][0])
        self.assertEqual("01/12/2019", qs["date_end"][0])
        self.assertEqual(2, len(movements))
        self.assertEqual(datetime(2019, 1, 12), movements[0].date)
        self.assertEqual(datetime(2019, 7, 5), movements[1].date)

    @respx.mock
    def test_get_credit_cards(self):
        self.mock_get_request(
            respx,
            "/credit-card/",
            json={
                "credit_cards": [
                    {
                        "balance_dollar": 67.89,
                        "balance_local": 12345.42,
                        "close_date": "04/11/2019",
                        "due_date": "20/11/2019",
                        "id": "EcebS0rIZ5NdJNzS4XHmuOnHvSsI72TSA3j/8drzYYHtW1sQbpz5Hc",
                        "name": "Vi Int Sumaclub Plus",
                        "number": "770012345678",
                    }
                ],
                "status": "success",
            },
        )
        session_key = "test_session_key"
        session = self.client.banking.get_session(session_key)
        cards = session.get_credit_cards()
        last_request = respx.calls.last.request
        self.assertEqual("/credit-card/", last_request.url.path)
        self.assertEqual(session_key, last_request.headers["X-Session-Key"])
        self.assertEqual(1, len(cards))
        self.assertEqual("Vi Int Sumaclub Plus", cards[0].name)
        self.assertEqual("770012345678", cards[0].number)
        self.assertEqual(datetime(2019, 11, 20), cards[0].due_date)

    @respx.mock
    def test_get_credit_card_movements(self):
        self.mock_get_request(
            respx,
            "/credit-card/1234567/movements",
            json={
                "movements": [
                    {
                        "credit": "",
                        "date": "12/01/2019",
                        "debit": 3500,
                        "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.C. ",
                        "id": "-890185180",
                        "reference": "000000005084",
                    },
                    {
                        "credit": "",
                        "date": "05/07/2019",
                        "debit": 16000,
                        "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.H Y ",
                        "id": "1024917397",
                        "reference": "000000002931",
                    },
                ],
                "status": "success",
            },
        )
        session_key = "test_session_key"
        card_number = "1234567"
        currency_code = "USD"
        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        card = CreditCard(
            self.client.banking,
            session_key,
            CreditCardModel(
                id="12345",
                name="Cuenta total",
                number=card_number,
                close_date=datetime(2019, 11, 4),
                due_date=datetime(2019, 11, 20),
                balance_local=12345.42,
                balance_dollar=67.89,
            ),
        )
        movements = card.get_movements(currency_code, date_start, date_end)
        last_request = respx.calls.last.request
        qs = parse_qs(urlparse(str(last_request.url)).query)
        self.assertEqual("/credit-card/1234567/movements", last_request.url.path)
        self.assertEqual(session_key, last_request.headers["X-Session-Key"])
        self.assertEqual(currency_code, qs["currency"][0])
        self.assertEqual("01/01/2019", qs["date_start"][0])
        self.assertEqual("01/12/2019", qs["date_end"][0])
        self.assertEqual(2, len(movements))
        self.assertEqual(datetime(2019, 1, 12), movements[0].date)
        self.assertEqual(datetime(2019, 7, 5), movements[1].date)

    @respx.mock
    def test_get_providers(self):
        self.mock_get_request(
            respx,
            "/provider/",
            json={
                "providers": [
                    {"code": "test", "country": "UY", "name": "Test Provider"}
                ],
                "status": "success",
            },
        )
        session = self.client.banking.new_session()
        providers = session.get_providers()
        self.assertEqual(1, len(providers))
        self.assertEqual("test", providers[0].code)
        self.assertEqual("UY", providers[0].country)
        self.assertEqual("Test Provider", providers[0].name)

    @respx.mock
    def test_get_provider_detail(self):
        self.mock_get_request(
            respx,
            "/provider/test/",
            json={
                "provider": {
                    "auth_fields": [
                        {
                            "name": "username",
                            "type": "text",
                            "interactive": False,
                            "optional": False,
                            "label_es": "Usuario",
                            "label_en": "Username",
                        },
                        {
                            "name": "password",
                            "type": "password",
                            "interactive": False,
                            "optional": False,
                            "label_es": "Contraseña",
                            "label_en": "Password",
                        },
                        {
                            "name": "personal_question",
                            "type": "text",
                            "interactive": True,
                            "optional": False,
                            "label_es": "Pregunta personal",
                            "label_en": "Personal Question",
                        },
                        {
                            "name": "otp",
                            "type": "text",
                            "interactive": True,
                            "optional": False,
                            "label_es": "Token OTP",
                            "label_en": "OTP Token",
                        },
                    ],
                    "name": "test",
                    "aliases": ["alias_test"],
                    "country": "UY",
                    "endpoints_status": None,
                    "account_type": [
                        {
                            "name": "pers",
                            "label_es": "Cuenta Personal",
                            "label_en": "Personal Account",
                        },
                        {
                            "name": "corp",
                            "label_es": "Cuenta Corporativa",
                            "label_en": "Corporate Account",
                        },
                    ],
                    "logo": "https://providers.prometeoapi.com/logos/test.png",
                    "bank": {
                        "code": "test",
                        "name": "Banco Test Prometeo",
                        "logo": "https://providers.prometeoapi.com/logos/test.png",
                    },
                    "methods": {
                        "accounts": True,
                        "credit_cards": True,
                        "accounts_movements": True,
                        "credit_cards_movements": True,
                        "personal_info": True,
                        "transfers": True,
                        "enrollments": True,
                    },
                },
                "status": "success",
            },
        )
        session = self.client.banking.new_session()
        provider = session.get_provider_detail("test")
        self.assertEqual("UY", provider.country)
        self.assertEqual("test", provider.name)
        self.assertEqual(4, len(provider.auth_fields))

    @respx.mock
    def test_get_provider_detail_filtered_options(self):
        self.mock_get_request(
            respx,
            "/provider/santander_pers_uy/?key=type&value=UY",
            "provider_details_santander",
        )
        session = self.client.banking.new_session()
        provider = session.get_provider_detail("santander_pers_uy", "type", "UY")
        self.assertEqual("UY", provider.country)
        self.assertEqual("santander_pers_uy", provider.name)
        self.assertEqual(4, len(provider.auth_fields))

    @respx.mock
    def test_provider_doesnt_exist(self):
        self.mock_get_request(
            respx,
            "/provider/invalid/",
            status_code=404,
            json={
                "status": "provider_doesnt_exist",
            },
        )
        with self.assertRaises(exceptions.NotFoundError):
            session = self.client.banking.new_session()
            session.get_provider_detail("invalid")

    @respx.mock
    def test_logout(self):
        self.mock_get_request(respx, "/logout/", json={"status": "logged_out"})
        session_key = "test_session_key"
        session = self.client.banking.get_session(session_key)
        session.logout()
        last_request = respx.calls.last.request
        self.assertEqual("/logout/", last_request.url.path)
        self.assertEqual(session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_preprocess_transfer(self):
        self.mock_post_request(
            respx,
            "/transfer/preprocess",
            json={
                "result": {
                    "approved": True,
                    "authorization_devices": [
                        {"data": ["F-4", "B-2", "G-7"], "type": "cardCode"},
                        {"data": None, "type": "pin"},
                    ],
                    "message": None,
                    "request_id": "0b7d6b32d1be4c11bde21e7ddc08cc36",
                },
                "status": "success",
            },
        )
        session_key = "test_session_key"
        origin_account = "002206345988"
        destination_institution = "0"
        destination_account = "001002363321"
        currency = "UYU"
        amount = "1.3"
        concept = "descripcion de transferencia"
        destination_owner_name = "John Doe"
        branch = "62"
        session = self.client.banking.get_session(session_key)
        preprocess = session.preprocess_transfer(
            origin_account,
            destination_institution,
            destination_account,
            currency,
            amount,
            concept,
            destination_owner_name,
            branch,
        )
        self.assertEqual(True, preprocess.approved)
        self.assertEqual(3, len(preprocess.authorization_devices[0].data))
        self.assertEqual("cardCode", preprocess.authorization_devices[0].type)
        self.assertEqual("0b7d6b32d1be4c11bde21e7ddc08cc36", preprocess.request_id)
        self.assertEqual(None, preprocess.message)

    @respx.mock
    def test_confirm_transfer(self):
        self.mock_post_request(
            respx,
            "/transfer/confirm",
            json={
                "status": "success",
                "transfer": {
                    "message": "Transferencia confirmada con exito",
                    "success": True,
                },
            },
        )
        session_key = "test_session_key"
        request_id = "0b7d6b32d1be4c11bde21e7ddc08cc36"
        authorization_type = "cardCode"
        authorization_data = "1, 2, 3"
        session = self.client.banking.get_session(session_key)
        confirmation = session.confirm_transfer(
            request_id, authorization_type, authorization_data
        )
        self.assertEqual(True, confirmation.success)
        self.assertNotEqual(None, confirmation.message)

    @respx.mock
    def test_list_transfer_institutions(self):
        self.mock_get_request(
            respx,
            "/transfer/destinations",
            json={
                "destinations": [
                    {"id": 0, "name": "SANTANDER"},
                    {"id": 1, "name": "B.R.O.U."},
                    {"id": 91, "name": "B.H.U."},
                    {"id": 110, "name": "BANDES"},
                ],
                "status": "success",
            },
        )
        session_key = "test_session_key"
        session = self.client.banking.get_session(session_key)
        institutions = session.list_transfer_institutions()
        self.assertNotEqual(0, len(institutions))

    @respx.mock
    def test_invalid_session_key(self):
        self.mock_get_request(
            respx, "/account/", json={"message": "Invalid key", "status": "error"}
        )
        with self.assertRaises(exceptions.InvalidSessionKeyError):
            session = self.client.banking.new_session()
            session.get_accounts()

    @respx.mock
    def test_generic_client_error(self):
        self.mock_get_request(
            respx,
            "/account/",
            json={"message": "Some generic error", "status": "error"},
        )
        with self.assertRaises(banking_exceptions.BankingClientError):
            session = self.client.banking.new_session()
            session.get_accounts()
