from prometeo import exceptions


class PaymentClientError(exceptions.PrometeoError):
    pass


class PaymentInvalidParameterClientError(PaymentClientError):
    def __init__(self, param, message):
        self.param = param
        self.message = message
