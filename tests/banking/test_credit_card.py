import unittest
from datetime import datetime

from prometeo.banking.client import BankingAPIClient, CreditCard
from prometeo.banking.models import CreditCard as CreditCardModel

from six.moves.urllib.parse import parse_qs, urlparse
import requests_mock


@requests_mock.Mocker()
class TestCreditCard(unittest.TestCase):

    def setUp(self):
        client = BankingAPIClient('test_api_key', 'testing')
        self.session_key = 'test_session_key'
        card = CreditCardModel(
            id='12345',
            name='Cuenta total',
            number='001234567890',
            close_date=datetime(2019, 11, 4),
            due_date=datetime(2019, 11, 20),
            balance_local=12345.42,
            balance_dollar=67.89,
        )
        self.card = CreditCard(client, self.session_key, card)

    def test_get_movements(self, m):
        m.get('/credit-card/001234567890/movements', json={
            "movements": [
                {
                    "credit": "",
                    "date": "12/01/2017",
                    "debit": 3500,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO",
                    "id": -890185180,
                    "reference": "000000005084",
                    "extra_data": None
                },
                {
                    "credit": "",
                    "date": "05/01/2017",
                    "debit": 16000,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO",
                    "id": 1024917397,
                    "reference": "000000002931",
                    "extra_data": None
                },
            ],
            "status": "success"
        })

        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        movements = self.card.get_movements('USD', date_start, date_end)
        qs = parse_qs(urlparse(m.last_request.url).query)
        self.assertEqual(self.session_key, qs['key'][0])
        self.assertEqual('USD', qs['currency'][0])
        self.assertEqual('01/01/2019', qs['date_start'][0])
        self.assertEqual('01/12/2019', qs['date_end'][0])
        self.assertEqual(2, len(movements))
