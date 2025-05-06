from prometeo.banking.client import BankingAPIClient, Session
from tests.base_test_case import BaseTestCase
import respx


class TestSession(BaseTestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        client = BankingAPIClient("test_api_key", "sandbox")
        self.session_key = "test_session_key"
        self.session = Session(client, "logged_in", self.session_key)

    @respx.mock
    def test_get_accounts(self):
        self.mock_get_request(respx, "/account/", "get_accounts")
        accounts = self.session.get_accounts()
        last_request = respx.calls.last.request
        self.assertEqual(2, len(accounts))
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_get_credit_cards(self):
        self.mock_get_request(respx, "/credit-card/", "get_credit_cards")
        cards = self.session.get_credit_cards()
        last_request = respx.calls.last.request
        self.assertEqual(1, len(cards))
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_restore_session(self):
        self.mock_get_request(respx, "/account/", "get_accounts")

        session_key = "test_restored_key"
        session = self.client.banking.get_session(session_key)

        session.get_accounts()
        last_request = respx.calls.last.request
        self.assertEqual(session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_logout(self):
        self.mock_get_request(respx, "/logout/", "successful_logout")

        self.session.logout()
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_preprocess_transfer(self):
        self.mock_post_request(respx, "/transfer/preprocess", "preprocess_transfer")
        origin_account = "002206345988"
        destination_institution = "0"
        destination_account = "001002363321"
        currency = "UYU"
        amount = "1.3"
        concept = "descripcion de transferencia"
        destination_owner_name = "John Doe"
        branch = "62"
        self.session.preprocess_transfer(
            origin_account,
            destination_institution,
            destination_account,
            currency,
            amount,
            concept,
            destination_owner_name,
            branch,
        )
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_confirm_transfer(self):
        self.mock_post_request(respx, "/transfer/confirm", "confirm_transfer")
        request_id = "0b7d6b32d1be4c11bde21e7ddc08cc36"
        authorization_type = "cardCode"
        authorization_data = "1, 2, 3"
        self.session.confirm_transfer(
            request_id, authorization_type, authorization_data
        )
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])

    @respx.mock
    def test_list_transfer_institutions(self):
        self.mock_get_request(
            respx, "/transfer/destinations", "list_transfer_institutions"
        )
        self.session.list_transfer_institutions()
        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])
