from .banking import BankingAPIClient
from .curp import CurpAPIClient
from .dian import DianAPIClient
from .sat import SatAPIClient
from .payment import PaymentAPIClient


class Client(object):
    def __init__(self, api_key, environment="sandbox"):
        self._api_key = api_key
        self._environment = environment
        self._banking = None
        self._dian = None
        self._sat = None
        self._curp = None
        self._payment = None

    @property
    def banking(self):
        if self._banking is None:
            self._banking = BankingAPIClient(self._api_key, self._environment)
        return self._banking

    @property
    def dian(self):
        if self._dian is None:
            self._dian = DianAPIClient(self._api_key, self._environment)
        return self._dian

    @property
    def sat(self):
        if self._sat is None:
            self._sat = SatAPIClient(self._api_key, self._environment)
        return self._sat

    @property
    def curp(self):
        if self._curp is None:
            self._curp = CurpAPIClient(self._api_key, self._environment)
        return self._curp

    @property
    def payment(self):
        if self._payment is None:
            self._payment = PaymentAPIClient(self._api_key, self._environment)
        return self._payment
