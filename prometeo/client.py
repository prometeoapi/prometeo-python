from .banking import BankingAPIClient


class Client(object):

    def __init__(self, api_key, environment='testing'):
        self._api_key = api_key
        self._environment = environment
        self._banking = None

    @property
    def banking(self):
        if self._banking is None:
            self._banking = BankingAPIClient(
                self._api_key, self._environment
            )
        return self._banking
