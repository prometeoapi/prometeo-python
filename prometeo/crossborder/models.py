from typing import Union, List, Optional
from pydantic import BaseModel, field_validator
from enum import Enum
from datetime import datetime


class BaseEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"{value!r} is not a valid {cls.__name__}")


class TaxIdTypeBR(BaseEnum):
    cnpj = "cnpj"
    cpf = "cpf"


class TaxIdTypeMX(BaseEnum):
    rfc = "rfc"
    curp = "curp"


class TaxIdTypePE(BaseEnum):
    ruc = "ruc"
    le = "le"
    dni = "dni"
    lm = "lm"
    pas = "pas"
    ce = "ce"


class PayinStatesEnum(BaseEnum):
    created = "created"
    initiated = "initiated"
    pending = "pending"
    rejected = "rejected"
    settled = "settled"
    refunded = "refunded"
    cancelled = "cancelled"


class PayoutStatesEnum(BaseEnum):
    created = "created"
    initiated = "initiated"
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"
    settled = "settled"
    cancelled = "cancelled"


class PayoutTransferState(BaseModel):
    state: PayoutStatesEnum
    timestamp: datetime
    message: Optional[str] = None


class PayinTransferState(BaseModel):
    state: PayinStatesEnum
    timestamp: datetime
    message: Optional[str] = None


class AccountFormatEnum(BaseEnum):
    clabe = "clabe"
    iban = "iban"
    cci = "cci"


class PayinTransferMethods(BaseEnum):
    transfer = "transfer"
    qr = "qr"


class Bank(BaseModel):
    name: str
    code: str
    bicfi: str
    country: str


class VirtualAccountDetails(BaseModel):
    account_format: Optional[Union[str, AccountFormatEnum]] = None
    account_number: str
    name: Optional[str] = None
    branch: Optional[str] = None
    bank: Optional[Bank] = None


class QRCodeDetails(BaseModel):
    emv_code: str
    img: str
    external_link: str
    expire_date: datetime

    @field_validator("expire_date", mode="before")
    def fix_utc(cls, v):
        if isinstance(v, str) and v.endswith(" UTC"):
            v = v.replace(" UTC", "+00:00")
        return v


class AccountDetails(BaseModel):
    account_number: str
    branch: Optional[str] = None
    owner_name: str
    account_format: AccountFormatEnum
    tax_id_type: str
    tax_id: str
    bank: Bank


class WithdrawalAccountDetailsResponse(BaseModel):
    id: Optional[str] = None
    account_format: Optional[AccountFormatEnum] = None
    account_number: str
    validation_status: Optional[str] = None
    description: Optional[str] = None
    selected: Optional[bool] = None
    branch: Optional[str] = None
    bank: Optional[Union[str, Bank]] = None


class PayinCustomer(BaseModel):
    name: str
    tax_id_type: Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE]
    tax_id: str
    external_id: str
    virtual_account: Optional[VirtualAccountDetails] = None
    qr: Optional[QRCodeDetails] = None


class Customer(BaseModel):
    id: str
    name: str
    tax_id_type: Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE]
    tax_id: str
    external_id: str
    withdrawal_accounts: Optional[List[WithdrawalAccountDetailsResponse]] = None
    virtual_accounts: Optional[List[VirtualAccountDetails]] = None
    qrs: Optional[List[QRCodeDetails]] = None


class IntentData(BaseModel):
    id: str
    external_id: str
    concept: str
    currency: str
    amount: float
    reference: Optional[str] = None
    customer: PayinCustomer
    destination: AccountDetails
    events: List[PayinTransferState]


class FXQuoteData(BaseModel):
    amount: Union[int, float]
    pair: str


class FXQuoteDataResponse(BaseModel):
    id: str
    amount: Union[int, float]
    net_amount: Union[float, int]
    target_amount: Union[float, int]
    currency: str
    target_currency: str
    expires_at: str


class IntentDataResponse(BaseModel):
    id: str
    customer: PayinCustomer
    quote: Optional[FXQuoteDataResponse] = None


class AccountTransaction(BaseModel):
    number: Optional[str] = None
    format: Optional[AccountFormatEnum] = None


class TaxInformation(BaseModel):
    type: Optional[str] = None
    tax_id: Optional[str] = None


class AccountDetailsTransaction(BaseModel):
    account_details: AccountTransaction
    tax_information: TaxInformation
    beneficiary_name: Optional[str] = None


class Transaction(BaseModel):
    id: str
    amount: float
    timestamp: datetime
    detail: Optional[str] = None
    type: str
    reference: str
    state: str
    origin: AccountDetailsTransaction
    destination: AccountDetailsTransaction


class WithdrawalAccountInput(BaseModel):
    account_format: AccountFormatEnum
    account_number: str
    description: Optional[str] = None
    selected: bool
    branch: Optional[str] = None
    bicfi: Optional[str] = None


class CreatePayoutTransferResponse(BaseModel):
    id: str
    customer: Customer


class CustomerAccountDetails(BaseModel):
    id: str
    selected: Optional[bool]
    account_format: AccountFormatEnum
    account_number: str
    branch: Optional[str] = None
    bank: Union[str, Bank]


class CustomerInput(BaseModel):
    name: Optional[str] = None
    tax_id_type: Optional[Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE]] = None
    tax_id: Optional[str] = None
    external_id: Optional[str] = None
    withdrawal_account: Optional[WithdrawalAccountInput] = None


class IntentDataRequest(BaseModel):
    destination_id: str
    concept: str
    currency: str
    payment_method: Optional[Union[str, PayinTransferMethods]]
    amount: float
    external_id: str
    customer: Union[str, CustomerInput]
    country: Optional[str] = None
    quote: Optional[str] = None


class CreatePayoutTransferRequest(BaseModel):
    description: str
    external_id: str
    origin: str
    amount: float
    customer: Union[str, CustomerInput]


class RefundIntentInput(BaseModel):
    intent_id: str
    external_id: str
    amount: float


class PayoutCustomer(BaseModel):
    name: str
    tax_id_type: Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE]
    tax_id: str
    external_id: str
    withdrawal_account: WithdrawalAccountDetailsResponse


class CustomerResponse(BaseModel):
    id: str
    name: str
    tax_id_type: Union[TaxIdTypeBR, TaxIdTypeMX, TaxIdTypePE]
    tax_id: str
    external_id: str
    withdrawal_accounts: Optional[List[CustomerAccountDetails]] = None
    virtual_accounts: Optional[List[VirtualAccountDetails]] = None
    qrs: Optional[List[QRCodeDetails]] = None


class PayinTransferState(BaseModel):
    state: PayinStatesEnum
    timestamp: datetime
    message: Optional[str] = None


class PayoutTransfer(BaseModel):
    id: str
    customer: PayoutCustomer
    amount: float
    currency: Optional[str] = None
    reference: Optional[str] = None
    events: List[PayoutTransferState]


class PayoutTransferInput(BaseModel):
    origin: str
    description: str
    currency: str
    amount: float
    external_id: str
    customer: Union[str, CustomerInput]


class PayoutTransferResponse(BaseModel):
    id: str
    customer: PayoutCustomer


class Account(BaseModel):
    id: str
    local_account_number: str
    balance: float
    available_balance: float
    currency: str
    country: str
    active: bool


class VoucherDataEvent(BaseModel):
    key_tracing: str
    url: str


class ExchangeCurrencyRequest(BaseModel):
    amount: float
    pair: str


class PayloadError(BaseModel):
    code: str
    message: str


class Payload(BaseModel):
    id: str
    amount: float
    concept: str
    currency: str
    intent_id: str
    transaction_id: str
    external_id: str
    origin: AccountDetails
    destination: AccountDetails
    voucher_data: VoucherDataEvent
    error: PayloadError


class Event(BaseModel):
    event_type: str
    event_id: str
    timestamp: datetime
    payload: Payload


class WebhookPayload(BaseModel):
    verify_token: str
    events: List[Event]
