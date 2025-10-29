from prometeo import exceptions


class CrossBorderClientError(exceptions.PrometeoError):
    """Base exception class for errors in the CrossBorderClient."""

    pass


class InvalidParameterError(CrossBorderClientError):
    def __init__(self, description):
        self.code = "X1001"
        self.type = "validation_error"
        self.status = "error"
        self.description = description
        self.message = "Validation error"

    def __str__(self):
        errors = []

        for item in self.description:
            field = item.get("field_name", "unknown_field")
            detail = item.get("error_detail", {})

            # If it's a dict of subfields (e.g. bicfi: [...])
            if isinstance(detail, dict):
                for subfield, messages in detail.items():
                    for msg in messages:
                        errors.append(f"{field}.{subfield}: {msg}")
            # If it's just a list of strings (non_field_errors case)
            elif isinstance(detail, list):
                for msg in detail:
                    errors.append(f"{field}: {msg}")
            else:
                errors.append(f"{field}: {detail}")

        error_str = "; ".join(errors)
        return f"{self.message} — {error_str}"


class ParseException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1002"
        self.type = "parse_error"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class Unauthorized(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1003"
        self.type = "authentication_error"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class PermissionException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1004"
        self.type = "permission_denied"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class NotFoundException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1005"
        self.type = "not_found"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class MethodNotAllowedException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1006"
        self.type = "method_not_allowed"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class NotAcceptableException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1007"
        self.type = "not_acceptable"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class UnsupportedMediaTypeException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1008"
        self.type = "unsupported_media_type"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class ThrottledException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1009"
        self.type = "throttling_error"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class CrossBorderAPIException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X1010"
        self.type = "api_error"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidAccountFormat(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2002"
        self.type = "invalid_account_type"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidTaxIdFormat(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2003"
        self.type = "invalid_tax_id_format"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class ProviderUnavailableException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2004"
        self.type = "provider_unavailable"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidFinancialInstitutionException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2005"
        self.type = "invalid_financial_institution"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidAmount(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2006"
        self.type = "invalid_amount"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidDateException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2007"
        self.type = "invalid_date"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class AuthorizationProviderException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2008"
        self.type = "provider_unavailable"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidProviderDataException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2009"
        self.type = "invalid_provider_data"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class PaymentAlreadyRefundedException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2010"
        self.type = "payment_already_refunded"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InsufficientAmountException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2011"
        self.type = "insufficient_amount"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class PaymentAmountExceedsOriginalException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2012"
        self.type = "payment_amount_exceeds_original"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class PaymentCannotBeRefundedException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2013"
        self.type = "payment_cannot_be_refunded"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class AccountDataNotMatchException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2014"
        self.type = "account_data_not_match"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidAccountException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2015"
        self.type = "invalid_account"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidQuoteException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2020"
        self.type = "invalid_quote"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class QuoteAlreadyUsedException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2021"
        self.type = "quote_already_used"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidQuoteAmountException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2031"
        self.type = "invalid_amount"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class InvalidQuoteCurrencyException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2032"
        self.type = "fx_rate_not_found"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"


class CurrencyPairNotAvailableException(CrossBorderClientError):
    def __init__(self, message):
        self.code = "X2033"
        self.type = "pricing_rule_not_found"
        self.status = "error"
        self.message = message

    def __str__(self):
        return f"{self.message}"
