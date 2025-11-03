import respx

from prometeo.crossborder.models import (
    FXQuoteData,
    IntentDataRequest,
    PayoutTransferInput,
    CustomerInput,
    WithdrawalAccountInput,
)
from tests.base_test_case import BaseTestCase
from prometeo.crossborder.exceptions import CrossBorderClientError
from datetime import datetime, timezone


class TestCrossBorderClient(BaseTestCase):
    @respx.mock
    async def test_create_intent_success(self):
        self.mock_post_request(respx, "/payin/intent", fixture_name="successful_intent")
        result = await self.client.crossborder.create_intent(
            IntentDataRequest(
                destination_id="destination_id",
                concept="concept",
                currency="currency",
                amount=100,
                customer="customer",
                payment_method="transfer",
                external_id="external_id",
            )
        )
        self.assertEqual(result.id, "f03758fe-5e54-48f6-a7b1-a6a55c8905e2")

    @respx.mock
    async def test_create_intent_success_with_customer(self):
        self.mock_post_request(
            respx,
            "/payin/intent",
            fixture_name="successful_intent_with_embebed_customer",
        )
        result = await self.client.crossborder.create_intent(
            IntentDataRequest(
                destination_id="destination_id",
                concept="concept",
                currency="MXN",
                amount=100,
                payment_method="transfer",
                customer=CustomerInput(
                    name="name",
                    tax_id_type="rfc",
                    tax_id="tax_id",
                    external_id="external_id",
                ),
                external_id="external_id",
            )
        )
        self.assertEqual(result.id, "80e61a67-1f0a-45b0-9cd8-4ab8e8788f5e")

    @respx.mock
    async def test_create_intent_parses_expire_date_with_utc_suffix(self):
        self.mock_post_request(respx, "/payin/intent", fixture_name="intent_pe")
        result = await self.client.crossborder.create_intent(
            IntentDataRequest(
                destination_id="dest",
                concept="Payment",
                currency="USD",
                amount=100,
                customer="customer",
                payment_method="transfer",
                external_id="ext",
            )
        )

        self.assertIsNotNone(result.customer.qr)
        self.assertEqual(
            result.customer.qr.expire_date,
            datetime(2025, 9, 20, 4, 59, 59, tzinfo=timezone.utc),
        )

    @respx.mock
    def test_create_intent_error(self):
        self.mock_post_request(respx, "/payin/intent", "error_intent")
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.create_intent(
                IntentDataRequest(
                    destination_id="f3676011-5203-43db-a760-115203e3db5e",
                    concept="concept",
                    currency="MXN",
                    amount=100,
                    payment_method="transfer",
                    customer="a7f9501c-6979-4400-92db-809d1d317e21",
                    external_id="external_id",
                )
            )
        self.assertIn("Validation error", cm.exception.message)

    @respx.mock
    async def test_create_intent_with_quote(self):
        self.mock_post_request(respx, "/payin/intent", "successful_intent_with_quote")
        result = await self.client.crossborder.create_intent(
            IntentDataRequest(
                destination_id="destination_id",
                concept="concept",
                currency="PEN",
                amount=100,
                payment_method="qr",
                customer=CustomerInput(
                    name="name",
                    tax_id_type="rfc",
                    tax_id="tax_id",
                    external_id="external_id",
                ),
                external_id="external_id",
                country="BR",
                quote="4b4d079e-c256-4b39-9aaf-907780cf5512",
            )
        )
        self.assertEqual(result.quote.id, "4b4d079e-c256-4b39-9aaf-907780cf5512")

    @respx.mock
    async def test_create_quote(self):
        self.mock_post_request(respx, "/fx/exchange", "create_quote_success")
        result = await self.client.crossborder.create_fx_quote(
            FXQuoteData(amount=10, pair="PEN/BRL")
        )
        self.assertEqual(result.id, "4b4d079e-c256-4b39-9aaf-907780cf5512")

    @respx.mock
    async def test_create_quote_invalid_par_error(self):
        self.mock_post_request(
            respx, "/fx/exchange", "create_quote_invalid_currency_par_error"
        )
        with self.assertRaises(CrossBorderClientError) as cm:
            await self.client.crossborder.create_fx_quote(
                FXQuoteData(amount=10, pair="VES/RUP")
            )
        self.assertIn(
            "The requested currency pair (XXXYYY) is not available",
            cm.exception.message,
        )

    @respx.mock
    def test_list_intents_success(self):
        self.mock_get_request(respx, "/payin/intent", "successful_intents")
        results = self.client.crossborder.list_intents()
        self.assertEqual(results[0].id, "f03758fe-5e54-48f6-a7b1-a6a55c8905e2")

    @respx.mock
    def test_list_intents_error(self):
        self.mock_get_request(respx, "/payin/intent", "error_intent_not_found")
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.list_intents()
        self.assertIn("Resource not found", cm.exception.message)

    @respx.mock
    def test_create_payout_success(self):
        self.mock_post_request(
            respx, "/payout/transfer", fixture_name="successful_payout"
        )
        result = self.client.crossborder.create_payout(
            PayoutTransferInput(
                origin="destination_id",
                description="concept",
                currency="currency",
                amount=100,
                external_id="external_id",
                customer="customer",
            )
        )
        self.assertEqual(result.id, "a7f9501c-6979-4400-92db-809d1d317e21")

    @respx.mock
    def test_create_payout_error(self):
        self.mock_post_request(respx, "/payout/transfer", "error_payout")
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.create_payout(
                PayoutTransferInput(
                    origin="destination_id",
                    description="concept",
                    currency="currency",
                    amount=100,
                    external_id="external_id",
                    customer="customer",
                )
            )
        self.assertIn("Insufficient amount for the transaction", cm.exception.message)

    @respx.mock
    def test_create_payout_success_with_customer(self):
        self.mock_post_request(
            respx,
            "/payout/transfer",
            fixture_name="successful_payout_with_embebed_customer",
        )
        result = self.client.crossborder.create_payout(
            PayoutTransferInput(
                origin="destination_id",
                description="concept",
                currency="currency",
                amount=100,
                external_id="external_id",
                customer=CustomerInput(
                    name="John Doe",
                    tax_id_type="rfc",
                    tax_id="JBND591220KI8",
                    external_id="external_id",
                ),
            )
        )
        self.assertEqual(result.id, "a624a513-45ab-4f2e-a748-0eb902e4f690")

    @respx.mock
    def test_get_payout_detail_success(self):
        self.mock_get_request(respx, "/payout/transfer/payout_id", "get_payout_detail")
        result = self.client.crossborder.get_payout("payout_id")
        self.assertEqual(result.id, "4d6c83e6-44ce-4963-ac83-e644ced9631c")

    @respx.mock
    def test_get_payout_detail_error(self):
        self.mock_get_request(respx, "/payout/transfer/payout_id", "error_payout")
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.get_payout("payout_id")
        self.assertIn("Insufficient amount for the transaction", cm.exception.message)

    @respx.mock
    def test_create_customer_success(self):
        self.mock_post_request(
            respx, "/customer", fixture_name="create_customer_success"
        )
        result = self.client.crossborder.create_customer(
            CustomerInput(
                name="name",
                tax_id_type="rfc",
                tax_id="tax_id",
                external_id="external_id",
                withdrawal_account=WithdrawalAccountInput(
                    account_format="clabe",
                    account_number="123456789012345678",
                    selected=True,
                ),
            )
        )
        self.assertEqual(result.id, "9c1dd10e-7c19-470d-9dd1-0e7c19670d64")

    @respx.mock
    def test_create_customer_error(self):
        self.mock_post_request(respx, "/customer", "create_customer_error")
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.create_customer(
                CustomerInput(
                    name="name",
                    tax_id_type="DNI",
                    tax_id="tax_id",
                    external_id="external_id",
                )
            )
        self.assertIn(
            "The submitted account number format is invalid", cm.exception.message
        )

    @respx.mock
    def test_add_withdrawal_account_customer_success(self):
        self.mock_post_request(
            respx,
            "/customer/customer_id/withdrawal_account",
            fixture_name="add_withdrawal_account_customer_success",
        )
        result = self.client.crossborder.add_withdrawal_account(
            "customer_id",
            WithdrawalAccountInput(
                account_format="clabe",
                account_number="123456789012345678",
                description="description",
                selected=True,
                branch="branch",
                bicfi="BBVAMXMM",
            ),
        )
        self.assertEqual(result.id, "9c1dd10e-7c19-470d-9dd1-0e7c19670d65")

    @respx.mock
    def test_add_withdrawal_account_customer_error(self):
        self.mock_post_request(
            respx,
            "/customer/customer_id/withdrawal_account",
            "add_withdrawal_account_customer_error",
        )
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.add_withdrawal_account(
                "customer_id",
                WithdrawalAccountInput(
                    account_format="clabe",
                    account_number="123456789012345678",
                    description="description",
                    selected=True,
                    branch="branch",
                    bicfi="BBVAMXMM",
                ),
            )
        self.assertIn("Validation error", cm.exception.message)

    @respx.mock
    def test_select_withdrawal_account_customer_success(self):
        self.mock_post_request(
            respx,
            "/customer/customer_id/withdrawal_account/account_id/select",
            fixture_name="select_withdrawal_account_customer_success",
        )
        result = self.client.crossborder.select_withdrawal_account(
            "customer_id",
            "account_id",
        )
        self.assertEqual(result.id, "9c1dd10e-7c19-470d-9dd1-0e7c19670d64")

    @respx.mock
    def test_select_withdrawal_account_customer_error(self):
        self.mock_post_request(
            respx,
            "/customer/customer_id/withdrawal_account/account_id/select",
            "select_withdrawal_account_customer_error",
        )
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.select_withdrawal_account(
                "customer_id",
                "account_id",
            )
        self.assertIn(
            "No WithdrawalAccount matches the given query.", cm.exception.message
        )

    @respx.mock
    def test_get_account_success(self):
        self.mock_get_request(
            respx, "/account/account_id", fixture_name="get_account_success"
        )
        result = self.client.crossborder.get_account("account_id")
        self.assertEqual(result.id, "f3676011-5203-43db-a760-115203e3db5e")

    @respx.mock
    def test_get_account_error(self):
        self.mock_get_request(respx, "/account/account_id", "get_account_error")
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.get_account("account_id")
        self.assertIn("Resource not found", cm.exception.message)

    @respx.mock
    def test_get_account_transactions_success(self):
        self.mock_get_request(
            respx,
            "/account/account_id/transactions",
            fixture_name="get_account_transactions",
        )
        result = self.client.crossborder.get_account_transactions("account_id")
        self.assertEqual(len(result), 1)

    @respx.mock
    def test_get_account_transactions_error(self):
        self.mock_get_request(
            respx, "/account/account_id/transactions", "get_account_transactions_error"
        )
        with self.assertRaises(CrossBorderClientError) as cm:
            self.client.crossborder.get_account_transactions("account_id")
        self.assertIn("Resource not found", cm.exception.message)
