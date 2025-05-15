from typing import Union, List, Optional
from pydantic import BaseModel


class AccountData(BaseModel):
    valid: bool
    message: Optional[str]
    account_number: Optional[str]
    bank_code: Optional[str]
    country_code: Optional[str]
    branch_code: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    beneficiary_name: Optional[str]
    account_currency: Optional[Union[str, List[str]]]
    account_type: Optional[str]
