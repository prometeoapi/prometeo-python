from prometeo import base_client, utils
from typing import List, Optional
from .exceptions import (
    CurrencyPairNotAvailableException,
    InvalidParameterError,
    InvalidQuoteAmountException,
    InvalidQuoteCurrencyException,
    InvalidQuoteException,
    ParseException,
    QuoteAlreadyUsedException,
    Unauthorized,
    PermissionException,
    NotFoundException,
    MethodNotAllowedException,
    NotAcceptableException,
    UnsupportedMediaTypeException,
    ThrottledException,
    CrossBorderAPIException,
    InvalidAccountFormat,
    InvalidTaxIdFormat,
    AuthorizationProviderException,
    InvalidFinancialInstitutionException,
    InvalidAmount,
    InvalidDateException,
    InvalidProviderDataException,
    PaymentAlreadyRefundedException,
    InsufficientAmountException,
    PaymentAmountExceedsOriginalException,
    ProviderUnavailableException,
    PaymentCannotBeRefundedException,
    AccountDataNotMatchException,
    InvalidAccountException,
    CrossBorderClientError,
)
from .models import (
    FXQuoteData,
    FXQuoteDataResponse,
    IntentData,
    IntentDataRequest,
    IntentDataResponse,
    RefundIntentInput,
    PayoutTransfer,
    PayoutTransferInput,
    PayoutTransferResponse,
    Customer,
    CustomerInput,
    CustomerResponse,
    WithdrawalAccountDetailsResponse,
    WithdrawalAccountInput,
    Account,
    Transaction,
)


SANDBOX_URL = "https://crossborder-api.sandbox.prometeoapi.com"
BETA_URL = "https://crossborder.beta.prometeoapi.com/v1/"
PRODUCTION_URL = "https://crossborder.secure.prometeoapi.net/v1/"


class CrossBorderAPIClient(base_client.BaseClient):
    """
    API Client for Cross Border API
    """

    ENVIRONMENTS = {
        "production": PRODUCTION_URL,
        "sandbox": SANDBOX_URL,
        "beta": BETA_URL,
        "custom": "",
    }

    def __init__(
        self,
        api_key,
        environment,
        raw_responses=False,
        proxy=None,
        custom_enviroment=None,
        *args,
        **kwargs,
    ):
        super().__init__(api_key, environment, raw_responses, proxy, *args, **kwargs)

        if environment == "custom" and custom_enviroment:
            self.ENVIRONMENTS["custom"] = custom_enviroment

    def on_error(self, response, data):
        if isinstance(data, dict):
            error_code = data.get("code")
            error_description = data.get("description")
            error_message = data.get("message")
        else:
            error_code = None
            error_description = None
            error_message = None

        if error_code == "X1001":
            raise InvalidParameterError(error_description)
        elif error_code == "X1002":
            raise ParseException(error_message)
        elif error_code == "X1003":
            raise Unauthorized(error_message)
        elif error_code == "X1004":
            raise PermissionException(error_message)
        elif error_code == "X1005":
            raise NotFoundException(error_message)
        elif error_code == "X1006":
            raise MethodNotAllowedException(error_message)
        elif error_code == "X1007":
            raise NotAcceptableException(error_message)
        elif error_code == "X1008":
            raise UnsupportedMediaTypeException(error_message)
        elif error_code == "X1009":
            raise ThrottledException(error_message)
        elif error_code == "X1010":
            raise CrossBorderAPIException(error_message)
        elif error_code == "X2002":
            raise InvalidAccountFormat(error_message)
        elif error_code == "X2003":
            raise InvalidTaxIdFormat(error_message)
        elif error_code == "X2004":
            raise ProviderUnavailableException(error_message)
        elif error_code == "X2005":
            raise InvalidFinancialInstitutionException(error_message)
        elif error_code == "X2006":
            raise InvalidAmount(error_message)
        elif error_code == "X2007":
            raise InvalidDateException(error_message)
        elif error_code == "X2008":
            raise AuthorizationProviderException(error_message)
        elif error_code == "X2009":
            raise InvalidProviderDataException(error_message)
        elif error_code == "X2010":
            raise PaymentAlreadyRefundedException(error_message)
        elif error_code == "X2011":
            raise InsufficientAmountException(error_message)
        elif error_code == "X2012":
            raise PaymentAmountExceedsOriginalException(error_message)
        elif error_code == "X2013":
            raise PaymentCannotBeRefundedException(error_message)
        elif error_code == "X2014":
            raise AccountDataNotMatchException(error_message)
        elif error_code == "X2015":
            raise InvalidAccountException(error_message)
        elif error_code == "X2020":
            raise InvalidQuoteException(error_message)
        elif error_code == "X2021":
            raise QuoteAlreadyUsedException(error_message)
        elif error_code == "X2031":
            raise InvalidQuoteAmountException(error_message)
        elif error_code == "X2032":
            raise InvalidQuoteCurrencyException(error_message)
        elif error_code == "X2033":
            raise CurrencyPairNotAvailableException(error_message)
        elif error_code:
            raise CrossBorderClientError(error_message)

    @utils.adapt_async_sync
    async def create_intent(self, data: IntentDataRequest) -> IntentDataResponse:
        response = await self.call_api(
            "POST", "payin/intent", json=data.dict(exclude_none=True)
        )
        return IntentDataResponse(**response)

    @utils.adapt_async_sync
    async def create_fx_quote(self, data: FXQuoteData) -> FXQuoteDataResponse:
        response = await self.call_api("POST", "fx/exchange", json=data.dict())
        return FXQuoteDataResponse(**response)

    @utils.adapt_async_sync
    async def list_intents(self) -> List[IntentData]:
        data = await self.call_api("GET", "payin/intent")
        return [IntentData(**intent) for intent in data.get("results", [])]

    @utils.adapt_async_sync
    async def get_intent(self, intent_id: str) -> IntentData:
        data = await self.call_api("GET", f"payin/intent/{intent_id}")
        return IntentData(**data)

    @utils.adapt_async_sync
    async def refund_intent(self, data: RefundIntentInput) -> PayoutTransferResponse:
        return PayoutTransferResponse(
            **await self.call_api("POST", "payin/refund", json=data.dict())
        )

    @utils.adapt_async_sync
    async def create_payout(self, data: PayoutTransferInput) -> PayoutTransferResponse:
        return PayoutTransferResponse(
            **await self.call_api("POST", "payout/transfer", json=data.dict())
        )

    @utils.adapt_async_sync
    async def get_payout(self, payout_id: str) -> PayoutTransfer:
        return PayoutTransfer(
            **await self.call_api("GET", f"payout/transfer/{payout_id}")
        )

    @utils.adapt_async_sync
    async def list_payouts(self) -> List[PayoutTransfer]:
        data = await self.call_api("GET", "payout/transfer")
        return [PayoutTransfer(**payout) for payout in data.get("results", [])]

    @utils.adapt_async_sync
    async def create_customer(self, data: CustomerInput) -> CustomerResponse:
        return CustomerResponse(
            **await self.call_api("POST", "customer", json=data.dict(exclude_none=True))
        )

    @utils.adapt_async_sync
    async def get_customer(self, customer_id: str) -> CustomerResponse:
        return CustomerResponse(**await self.call_api("GET", f"customer/{customer_id}"))

    @utils.adapt_async_sync
    async def get_customers(self, params: Optional[dict] = None) -> List[Customer]:
        data = await self.call_api("GET", "customer", params=params)
        return [Customer(**customer) for customer in data.get("results", [])]

    @utils.adapt_async_sync
    async def update_customer(
        self, customer_id: str, data: CustomerInput
    ) -> CustomerResponse:
        return CustomerResponse(
            **await self.call_api(
                "PATCH", f"customer/{customer_id}", json=data.dict(exclude_none=True)
            )
        )

    @utils.adapt_async_sync
    async def add_withdrawal_account(
        self, customer_id: str, data: WithdrawalAccountInput
    ) -> CustomerResponse:
        return CustomerResponse(
            **await self.call_api(
                "POST",
                f"customer/{customer_id}/withdrawal_account",
                json=data.dict(exclude_none=True),
            )
        )

    @utils.adapt_async_sync
    async def select_withdrawal_account(
        self, customer_id: str, account_id: str
    ) -> WithdrawalAccountDetailsResponse:
        return WithdrawalAccountDetailsResponse(
            **await self.call_api(
                "POST", f"customer/{customer_id}/withdrawal_account/{account_id}/select"
            )
        )

    @utils.adapt_async_sync
    async def get_accounts(self) -> List[Account]:
        data = await self.call_api("GET", "account")
        return [Account(**account) for account in data]

    @utils.adapt_async_sync
    async def get_account(self, account_id: str) -> Account:
        return Account(**await self.call_api("GET", f"account/{account_id}"))

    @utils.adapt_async_sync
    async def get_account_transactions(self, account_id: str) -> List[Transaction]:
        data = await self.call_api("GET", f"account/{account_id}/transactions")
        return [Transaction(**transaction) for transaction in data.get("results", [])]
