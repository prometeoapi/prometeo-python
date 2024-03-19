from datetime import datetime

from prometeo.banking.client import BankingAPIClient, CreditCard
from prometeo.banking.models import CreditCard as CreditCardModel

import respx
from tests.base_test_case import BaseTestCase


class TestCreditCard(BaseTestCase):
    def setUp(self):
        client = BankingAPIClient("test_api_key", "sandbox")
        self.session_key = "test_session_key"
        card = CreditCardModel(
            id="12345",
            name="Cuenta total",
            number="001234567890",
            close_date=datetime(2019, 11, 4),
            due_date=datetime(2019, 11, 20),
            balance_local=12345.42,
            balance_dollar=67.89,
        )
        self.card = CreditCard(client, self.session_key, card)

    @respx.mock
    def test_get_movements(self):
        self.mock_get_request(
            respx,
            "/credit-card/001234567890/movements",
            json={
                "movements": [
                    {
                        "credit": "",
                        "date": "12/01/2017",
                        "debit": 3500,
                        "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO",
                        "id": "-890185180",
                        "reference": "000000005084",
                        "extra_data": None,
                    },
                    {
                        "credit": "",
                        "date": "05/01/2017",
                        "debit": 16000,
                        "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO",
                        "id": 1024917397,
                        "reference": "000000002931",
                        "extra_data": None,
                    },
                ],
                "status": "success",
            },
        )

        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        movements = self.card.get_movements("USD", date_start, date_end)

        last_request = respx.calls.last.request
        self.assertEqual(self.session_key, last_request.headers["X-Session-Key"])
        self.assertEqual("USD", self.qs(last_request)["currency"][0])
        self.assertEqual("01/01/2019", self.qs(last_request)["date_start"][0])
        self.assertEqual("01/12/2019", self.qs(last_request)["date_end"][0])
        self.assertEqual(2, len(movements))
