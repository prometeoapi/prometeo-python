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
