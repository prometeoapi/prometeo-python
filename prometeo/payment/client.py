from prometeo import exceptions, base_client, utils
from .exceptions import PaymentInvalidParameterClientError
from typing import Optional, List
from .models import CreatePaymentIntentResponse, PaymentIntent


PRODUCTION_URL = "https://payment.prometeoapi.net"


class PaymentAPIClient(base_client.BaseClient):
    """
    API Client for Payment API
    """

    ENVIRONMENTS = {
        "production": PRODUCTION_URL,
    }

    def on_error(self, response, data):
        message = data.get("message")
        if response.status_code == 400 and message:
            raise exceptions.BadRequestError(data.get("message"))
        first_parameter = list(data.keys())[0]
        if response.status_code == 400 and first_parameter:
            raise PaymentInvalidParameterClientError(
                first_parameter, data.get(first_parameter)
            )

    @utils.adapt_async_sync
    async def create_intent(
        self,
        widget_id: str,
        currency: str,
        amount: str,
        external_id: Optional[str] = None,
        concept: Optional[str] = None,
        bank_codes: Optional[List[str]] = None,
    ) -> CreatePaymentIntentResponse:
        """
        Create payment intent.

        :param widget_id: The widget id
        :type widget_id: str

        :param currency: The payment currency
        :type currency: str

        :param amount: The payment amount
        :type amount: str

        :param external_id: The external id from merchant
        :type external_id: str

        :param concept: The payment concept
        :type concept: str

        :param bank_codes: Select Bank Codes to show in Widget
        :type bank_codes: List[str]

        :return: The payment intent id if it was created, None instead.
        :rtype: CreatePaymentIntentResponse
        """
        data = await self.call_api(
            "POST",
            "/api/v1/payment-intent/",
            json={
                "product_id": widget_id,
                "product_type": "widget",
                "currency": currency,
                "amount": amount,
                "external_id": external_id,
                "concept": concept,
                "bank_codes": bank_codes,
            },
        )
        return CreatePaymentIntentResponse(**data)

    @utils.adapt_async_sync
    async def get_transaction_data(self, intent_id: str) -> PaymentIntent:
        """
        Get transaction data from intent.

        :param intent_id: The intent id
        :type intent_id: str

        :return: The payment intent transaction data
        :rtype: PaymentIntent
        """
        data = await self.call_api("GET", f"/api/v1/payment-intent/{intent_id}")
        return PaymentIntent(**data)
