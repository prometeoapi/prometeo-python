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
        self, error_message, error_key
    ) -> Tuple[Optional[List[str]], str]:
        pattern = error_key + r" parameter: ([^.,]+(?:,\s[^.,]+)*)[.]?\s*([^.]*)"
        match = re.match(pattern, error_message)
        if match:
            parameters = match.group(1)
            return parameters.split(", "), error_message
        return None, error_message

    def on_error(self, response, data):
        errors = data.get("errors", {}) or {}
        error_message = errors.get("message")
        error_code = errors.get("code")
        error_key = ""

        if error_code == 400 and error_message:
            if "Invalid" in error_message:
                error_key = "Invalid"
                raise exceptions.InvalidParameterError(
                    *self.extract_invalid_parameters(error_message, error_key)
                )
            elif "Missing" in error_message:
                error_key = "Missing"
                raise exceptions.MissingParameterError(
                    *self.extract_invalid_parameters(error_message, error_key)
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
        document_type: Optional[str] = None,
        branch_code: Optional[str] = None,
        account_type: Optional[str] = None,
    ) -> AccountData:
        """
        Validate bank account information.

        :param account_number: The account number to be validated.
        :type account_number: str

        :param country_code: The country code associated with the account.
        :type country_code: str

        :param bank_code: The bank code if available.
        :type bank_code: Optional[str]

        :param document_number: The document number associated with the account.
        :type document_number: Optional[str]

        :param document_type: The document type associated with the account.
        :type document_type: Optional[str]

        :param branch_code: The branch code if available.
        :type branch_code: Optional[str]

        :param account_type: The account types.
        :type account_type: Optional[str]

        :return: An object containing validated account information.
        :rtype: AccountData
        :raises: Any exceptions raised during the validation process.
        """

        data = await self.call_api(
            "POST",
            "/validate-account/",
            data={
                "account_number": account_number,
                "country_code": country_code,
                "document_number": document_number,
                "document_type": document_type,
                "branch_code": branch_code,
                "bank_code": bank_code,
                "account_type": account_type,
            },
        )
        return AccountData(**data.get("data"))
