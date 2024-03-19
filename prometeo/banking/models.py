from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class Client(BaseModel):
    id: str
    name: str


class Account(BaseModel):
    id: str
    name: str
    number: str
    branch: str
    currency: str
    balance: float


class CreditCard(BaseModel):
    id: Union[str, int]
    name: str
    number: str
    close_date: Union[datetime, str]
    due_date: Union[datetime, str]
    balance_local: Union[float, str]
    balance_dollar: Union[float, str]


class Movement(BaseModel):
    id: Union[str, int]
    reference: str
    date: Union[datetime, str]
    detail: str
    debit: Optional[Union[float, str]]
    credit: Optional[Union[float, str]]
    extra_data: Optional[dict]


class Provider(BaseModel):
    code: str
    country: str
    name: str


class OTP(BaseModel):
    data: Optional[List[str]]
    type: str


class PreprocessTransfer(BaseModel):
    approved: bool
    authorization_devices: Optional[List[OTP]]
    message: Optional[str]
    request_id: str


class ConfirmTransfer(BaseModel):
    message: Optional[str]
    success: bool


class TransferInstitution(BaseModel):
    id: int
    name: str


class AuthFieldChoice(BaseModel):
    name: str
    type: str
    interactive: bool
    optional: bool
    label_es: str
    label_en: str
    choices: List[dict]
    default: Optional[str]


class AuthFieldText(BaseModel):
    name: str
    type: str
    interactive: bool
    optional: bool
    label_es: str
    label_en: str


class AuthFieldPassword(BaseModel):
    name: str
    type: str
    interactive: bool
    optional: bool
    label_es: str
    label_en: str


class EndpointStatus(BaseModel):
    endpoint: str
    status: str
    timestamp: str


class EndpointsStatus(BaseModel):
    test: List[EndpointStatus]
    prod: List[EndpointStatus]


class AccountType(BaseModel):
    name: str
    label_es: str
    label_en: str


class Bank(BaseModel):
    code: str
    name: str
    logo: str


class Methods(BaseModel):
    accounts: bool
    credit_cards: bool
    accounts_movements: bool
    credit_cards_movements: bool
    personal_info: bool
    transfers: bool
    enrollments: bool


class ProviderDetail(BaseModel):
    name: str
    aliases: List[str]
    country: str
    auth_fields: List[Union[AuthFieldChoice, AuthFieldText, AuthFieldPassword]]
    endpoints_status: Optional[EndpointsStatus]
    account_type: List[AccountType]
    logo: str
    bank: Bank
    methods: Optional[Methods]
