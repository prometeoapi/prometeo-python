from prometeo.banking.client import BankingAPIClient, Session
from tests.base_test_case import BaseTestCase

import requests_mock


@requests_mock.Mocker()
class TestSession(BaseTestCase):

    def setUp(self):
        super(TestSession, self).setUp()
        client = BankingAPIClient('test_api_key', 'testing')
        self.session_key = 'test_session_key'
        self.session = Session(client, 'logged_in', self.session_key)

    def test_get_accounts(self, m):
        self.mock_get_request(m, '/account/', 'get_accounts')
        accounts = self.session.get_accounts()
        self.assertEqual(2, len(accounts))
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])

    def test_get_credit_cards(self, m):
        self.mock_get_request(m, '/credit-card/', 'get_credit_cards')
        cards = self.session.get_credit_cards()
        self.assertEqual(1, len(cards))
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])

    def test_restore_session(self, m):
        self.mock_get_request(m, '/account/', 'get_accounts')

        session_key = 'test_restored_key'
        session = self.client.banking.get_session(session_key)

        session.get_accounts()
        self.assertEqual(session_key, m.last_request.qs['key'][0])

    def test_logout(self, m):
        self.mock_get_request(m, '/logout/', 'successful_logout')
        self.session.logout()
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])

    def test_preprocess_transfer(self, m):
        self.mock_post_request(m, '/transfer/preprocess', 'preprocess_transfer')
        origin_account = '002206345988'
        destination_institution = '0'
        destination_account = '001002363321'
        currency = 'UYU'
        amount = '1.3'
        concept = 'descripcion de transferencia'
        destination_owner_name = 'John Doe'
        branch = '62'
        self.session.preprocess_transfer(origin_account, destination_institution,
                                         destination_account, currency, amount,
                                         concept, destination_owner_name, branch)
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])

    def test_confirm_transfer(self, m):
        self.mock_post_request(m, '/transfer/confirm', 'confirm_transfer')
        request_id = '0b7d6b32d1be4c11bde21e7ddc08cc36'
        authorization_type = 'cardCode'
        authorization_data = '1, 2, 3'
        self.session.confirm_transfer(request_id, authorization_type,
                                      authorization_data)
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])

    def test_list_transfer_institutions(self, m):
        self.mock_get_request(m, '/transfer/destinations',
                              'list_transfer_institutions')
        self.session.list_transfer_institutions()
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])
