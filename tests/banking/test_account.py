import unittest
from datetime import datetime

from prometeo.banking.client import BankingAPIClient, Account
from prometeo.banking.models import Account as AccountModel

from six.moves.urllib.parse import parse_qs, urlparse
import requests_mock


@requests_mock.Mocker()
class TestAccount(unittest.TestCase):

    def setUp(self):
        client = BankingAPIClient('test_api_key', 'testing')
        self.session_key = 'test_session_key'
        account = AccountModel(
            id='12345',
            name='Cuenta total',
            number='001234567890',
            branch='02 - 18 De Julio',
            currency='UYU',
            balance=1234.95,
        )
        self.account = Account(client, self.session_key, account)

    def test_get_movements(self, m):
        m.get('/movement/', json={
            "movements": [
                {
                    "credit": "",
                    "date": "12/01/2019",
                    "debit": 3500,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.C. ",
                    "id": -890185180,
                    "reference": "000000005084",
                    "extra_data": None
                },
                {
                    "credit": "",
                    "date": "05/07/2019",
                    "debit": 16000,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.H Y ",
                    "id": 1024917397,
                    "reference": "000000002931",
                    "extra_data": None
                },
            ],
            "status": "success",
        })
        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        movements = self.account.get_movements(date_start, date_end)
        qs = parse_qs(urlparse(m.last_request.url).query)
        self.assertEqual(self.session_key, qs['key'][0])
        self.assertEqual(self.account.number, qs['account'][0])
        self.assertEqual(self.account.currency, qs['currency'][0])
        self.assertEqual('01/01/2019', qs['date_start'][0])
        self.assertEqual('01/12/2019', qs['date_end'][0])
        self.assertEqual(2, len(movements))
