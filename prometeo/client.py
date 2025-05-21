from .banking import BankingAPIClient
from .curp import CurpAPIClient
from .dian import DianAPIClient
from .sat import SatAPIClient
from .payment import PaymentAPIClient
from .account_validation import AccountValidationAPIClient


class Client(object):
    def __init__(
        self,
        api_key,
        environment="sandbox",
        raw_responses=False,
        proxy=None,
        *args,
        **kwargs
    ):
        self._api_key = api_key
        self._environment = environment
        self._raw_responses = raw_responses
        self._proxy = proxy
        self._banking = None
        self._dian = None
        self._sat = None
        self._curp = None
        self._payment = None
        self._account_validation = None
        self._args = args
        self._kwargs = kwargs

    @property
    def banking(self):
        if self._banking is None:
            self._banking = BankingAPIClient(
                self._api_key,
                self._environment,
                self._raw_responses,
                self._proxy,
                *self._args,
                **self._kwargs
            )
        return self._banking

    @property
    def dian(self):
        if self._dian is None:
            self._dian = DianAPIClient(
                self._api_key,
                self._environment,
                self._raw_responses,
                self._proxy,
                *self._args,
                **self._kwargs
            )
        return self._dian

    @property
    def sat(self):
        if self._sat is None:
            self._sat = SatAPIClient(
                self._api_key,
                self._environment,
                self._raw_responses,
                self._proxy,
                *self._args,
                **self._kwargs
            )
        return self._sat

    @property
    def curp(self):
        if self._curp is None:
            self._curp = CurpAPIClient(
                self._api_key,
                self._environment,
                self._raw_responses,
                self._proxy,
                *self._args,
                **self._kwargs
            )
        return self._curp

    @property
    def payment(self):
        if self._payment is None:
            self._payment = PaymentAPIClient(
                self._api_key,
                self._environment,
                self._raw_responses,
                self._proxy,
                *self._args,
                **self._kwargs
            )
        return self._payment

    @property
    def account_validation(self):
        if self._account_validation is None:
            self._account_validation = AccountValidationAPIClient(
                self._api_key,
                self._environment,
                self._raw_responses,
                self._proxy,
                *self._args,
                **self._kwargs
            )
        return self._account_validation
