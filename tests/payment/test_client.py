from prometeo import exceptions
from prometeo.payment import exceptions as payment_exceptions
from tests.base_test_case import BaseTestCase

from prometeo import Client
import respx


class TestClient(BaseTestCase):
    def setUp(self):
        self.client = Client("test_key", "production")

    @respx.mock
    def test_create_intent_error_concept_too_long(self):
        self.mock_post_request(
            respx,
            "/api/v1/payment-intent/",
            json={
                "concept": ["Ensure this value has at most 20 characters (it has 32)."]
            },
            status_code=400,
        )
        with self.assertRaises(
            payment_exceptions.PaymentInvalidParameterClientError
        ) as e:
            self.client.payment.create_intent(
                widget_id="BBBBB-d66a-4234-8ea1-3e3ce1c0935b",
                currency="USD",
                amount="1.00",
                external_id=None,
                concept="TOO LONG CONCEPT MAX IS 20 CHARS",
            )

        self.assertIn("concept", e.exception.param)
        self.assertIn(
            "Ensure this value has at most 20 characters (it has 32).",
            e.exception.message,
        )

    @respx.mock
    def test_create_intent_error_inexistent_bank_code(self):
        self.mock_post_request(
            respx,
            "/api/v1/payment-intent/",
            json={
                "bank_codes": ["Object with code=inexistent_bank_code does not exist."]
            },
            status_code=400,
        )
        with self.assertRaises(
            payment_exceptions.PaymentInvalidParameterClientError
        ) as e:
            self.client.payment.create_intent(
                widget_id="BBBBB-d66a-4234-8ea1-3e3ce1c0935b",
                currency="USD",
                amount="1.00",
                external_id=None,
                concept="PROM123452 REF454243",
                bank_codes=["inexistent_bank"],
            )

        self.assertIn("bank_codes", e.exception.param)
        self.assertIn(
            "Object with code=inexistent_bank_code does not exist.", e.exception.message
        )

    @respx.mock
    def test_create_intent_successfully(self):
        self.mock_post_request(
            respx, "/api/v1/payment-intent/", "create_intent_response_success"
        )
        data = self.client.payment.create_intent(
            widget_id="BBBBB-d66a-4234-8ea1-3e3ce1c0935b",
            currency="USD",
            amount="1.00",
            external_id=None,
            concept="PROM123452 REF454243",
            bank_codes=["test"],
        )
        self.assertEqual(data.intent_id, "52abd9b2-7a8d-4e8b-b724-0b68701d2e0e")

    @respx.mock
    def test_valid_intent_id_unpaid(self):
        intent_id = "bea71e55-a1ec-4e5f-a5c0-c0e10b1a571c"
        self.mock_get_request(
            respx, f"/api/v1/payment-intent/{intent_id}", "valid_intent_unpaid"
        )

        data = self.client.payment.get_transaction_data(intent_id)
        self.assertEqual(1118.86, data.amount)
        self.assertEqual("PEN", data.currency)

    @respx.mock
    def test_valid_intent_id_paid(self):
        intent_id = "9999e375-9999-4da0-a4fd-85e5a04c9999"
        self.mock_get_request(
            respx, f"/api/v1/payment-intent/{intent_id}", "valid_intent_paid"
        )

        data = self.client.payment.get_transaction_data(intent_id)
        self.assertEqual(133.89, data.amount)
        self.assertEqual("UYU", data.currency)

    @respx.mock
    def test_invalid_intent_id(self):
        intent_id = "bea71e55-a1ec-4e5f-a5c0-c0e10b1a571c"
        self.mock_get_request(
            respx,
            f"/api/v1/payment-intent/{intent_id}",
            json={"message": "The payment intent id is not valid"},
            status_code=400,
        )
        with self.assertRaises(exceptions.BadRequestError):
            self.client.payment.get_transaction_data(intent_id)
