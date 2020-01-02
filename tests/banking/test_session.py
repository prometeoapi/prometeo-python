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
        m.get('/account/', json={
            "accounts": [
                {
                    "balance": 1234.95,
                    "branch": "02 - 18 De Julio",
                    "currency": "UYU",
                    "id": "hash1",
                    "name": "Cuenta total",
                    "number": "001234567890"
                },
                {
                    "balance": 53.96,
                    "branch": "61 - Ciudad Vieja",
                    "currency": "USD",
                    "id": "hash4",
                    "name": "Caja De Ahorro Atm",
                    "number": "004327567890"
                }
            ],
            "status": "success",
        })
        accounts = self.session.get_accounts()
        self.assertEqual(2, len(accounts))
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])

    def test_get_credit_cards(self, m):
        m.get('/credit-card/', json={
            "credit_cards": [
                {
                    "balance_dollar": 67.89,
                    "balance_local": 12345.42,
                    "close_date": "04/11/2019",
                    "due_date": "20/11/2019",
                    "id": "EcebS0rIZ5NdJNzS4XHmuOnHvSsI72TSA3j/8drzYYHtW1sQbpz5Hc",
                    "name": "Vi Int Sumaclub Plus",
                    "number": "770012345678"
                }
            ],
            "status": "success",
        })
        cards = self.session.get_credit_cards()
        self.assertEqual(1, len(cards))
        self.assertEqual(self.session_key, m.last_request.qs['key'][0])
