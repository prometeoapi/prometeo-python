

class PrometeoError(Exception):
    def __init__(self, message):
        self.message = message


class ClientError(PrometeoError):
    pass


class WrongCredentialsError(PrometeoError):
    pass


class UnauthorizedError(PrometeoError):
    pass


class ForbiddenError(PrometeoError):
    pass


class BadRequestError(PrometeoError):
    pass


class NotFoundError(PrometeoError):
    pass


class InternalAPIError(PrometeoError):
    pass


class ProviderUnavailableError(PrometeoError):
    pass


class InvalidSessionKeyError(PrometeoError):
    pass
