from prometeo import exceptions, base_client, utils
from .exceptions import (
    InvalidAccountError,
    PendingValidationError,
    MethodNotAvailableError,
    CommunicationError,
    BankProviderNotAvailableError,
    CountryNotAvailableError,
    InvalidCurrencyAccountError,
)
from .codes import BankCodes, ISOCode, AccountType
from typing import Optional, Union, List, Tuple
from .models import AccountData
import re


PRODUCTION_URL = "https://account-validation.prometeoapi.net"
BETA_URL = "https://account-validation.beta.prometeoapi.com"
SANDBOX_URL = "https://account-validation.sandbox.prometeoapi.com"


class AccountValidationAPIClient(base_client.BaseClient):
    """
    API Client for Account Validation API
    """

    ENVIRONMENTS = {
        "production": PRODUCTION_URL,
        "beta": BETA_URL,
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
        super().on_error(response, data)

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
            elif "Cuenta credito en otra divisa" in error_message:
                raise InvalidCurrencyAccountError(error_message)

        elif error_code == 404:
            raise InvalidAccountError(error_message)
        elif error_code == 202:
            raise PendingValidationError(error_message)
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
        country_code: Union[str, ISOCode],
        bank_code: Optional[Union[str, BankCodes]] = None,
        document_number: Optional[str] = None,
        document_type: Optional[str] = None,
        branch_code: Optional[str] = None,
        account_type: Optional[Union[str, AccountType]] = None,
        beneficiary_name: Optional[str] = None,
    ) -> AccountData:
        """
        Validate bank account information.

        :param account_number: The account number to be validated.
        :type account_number: str

        :param country_code: The country code associated with the account.
        :type country_code: Union[str,ISOCode]

        :param bank_code: The bank code if available.
        :type bank_code: Optional[Union[str, BankCodes]]

        :param document_number: The document number associated with the account.
        :type document_number: Optional[str]

        :param document_type: The document type associated with the account.
        :type document_type: Optional[str]

        :param branch_code: The branch code if available.
        :type branch_code: Optional[str]

        :param account_type: The account type to consider.
        :type account_type: Optional[Union[str,AccountType]]

        :param beneficiary_name: Account owner's name.
        :type beneficiary_name: Optional[str]

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
                "beneficiary_name": beneficiary_name,
            },
        )

        return AccountData(**data.get("data"))
