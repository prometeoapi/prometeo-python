from prometeo import exceptions


class AccountValidationClientError(exceptions.PrometeoError):
    """Base exception class for errors in the AccountValidationClient."""

    pass


class InvalidAccountError(AccountValidationClientError):
    """Exception for invalid account error"""

    pass


class PendingValidationError(AccountValidationClientError):
    """Exception raised for pending validations"""

    pass


class CommunicationError(AccountValidationClientError):
    """Exception for communication-related errors."""

    pass


class MethodNotAvailableError(AccountValidationClientError):
    """Exception for method not available errors."""

    pass


class BankProviderNotAvailableError(AccountValidationClientError):
    """Exception for bank provider not available errors."""

    pass


class CountryNotAvailableError(AccountValidationClientError):
    """Exception for country not available errors."""

    pass


class InvalidParameterError(AccountValidationClientError):
    """Exception for invalid parameter errors."""

    pass
