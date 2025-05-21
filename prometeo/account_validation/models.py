from typing import Union, List, Optional
from pydantic import BaseModel
from .codes import BankCodes, ISOCode, AccountType, DocumentType


class AccountData(BaseModel):
    valid: bool
    message: Optional[str]
    account_number: Optional[str]
    bank_code: Optional[Union[str, BankCodes]]
    country_code: Optional[Union[str, ISOCode]]
    branch_code: Optional[str]
    document_type: Optional[Union[str, DocumentType]]
    document_number: Optional[str]
    beneficiary_name: Optional[str]
    account_currency: Optional[Union[str, List[str]]]
    account_type: Optional[Union[str, AccountType]]
