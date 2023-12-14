from prometeo import exceptions, base_client, utils
from .exceptions import (
    InvalidAccountError,
    PendingValidationError,
    MethodNotAvailableError,
    CommunicationError,
    BankProviderNotAvailableError,
    CountryNotAvailableError,
)
from typing import Optional, List, Tuple
from .models import AccountData
import re


PRODUCTION_URL = "https://account-validation.prometeoapi.net"
SANDBOX_URL = "https://account-validation.sandbox.prometeoapi.com"


class AccountValidationAPIClient(base_client.BaseClient):
    """
    API Client for Account Validation API
    """

    ENVIRONMENTS = {
        "production": PRODUCTION_URL,
        "sandbox": SANDBOX_URL,
    }

    def extract_invalid_parameters(
        self, error_message
    ) -> Tuple[Optional[List[str]], str]:
        pattern = r"Invalid parameter: ([^.,]+(?:,\s[^.,]+)*)[.]?\s*([^.]*)"
        match = re.match(pattern, error_message)
        if match:
            parameters = match.group(1)
            message = match.group(2)
            return parameters.split(", "), message.strip()
        return None, None

    def on_error(self, response, data):
        errors = data.get("errors", {}) or {}
        error_message = errors.get("message")
        error_code = errors.get("code")

        if error_code == 400 and error_message:
            raise exceptions.InvalidParameterError(
                *self.extract_invalid_parameters(error_message)
            )
        elif error_code == 404:
            raise InvalidAccountError(error_message)
        elif error_code == 202:
            raise PendingValidationError(error_message)
        elif error_code == 500:
            raise exceptions.InternalAPIError(error_message, response.text)
        elif error_code == 503:
            raise CommunicationError(error_message)
        elif error_code == 512:
            raise MethodNotAvailableError(error_message)
        elif error_code == 513:
            raise BankProviderNotAvailableError(error_message)
        elif error_code == 514:
            raise CountryNotAvailableError(error_message)

    @utils.adapt_async_sync
    async def validate(
        self,
        account_number: str,
        country_code: str,
        bank_code: Optional[str] = None,
        document_number: Optional[str] = None,
        branch_code: Optional[str] = None,
        account_type: Optional[List[str]] = None,
    ) -> AccountData:
        data = await self.call_api(
            "POST",
            "/validate-account/",
            data={
                "account_number": account_number,
                "country_code": country_code,
                "document_number": document_number,
                "branch_code": branch_code,
                "bank_code": bank_code,
                "account_type": account_type,
            },
        )
        return AccountData(**data.get("data"))
