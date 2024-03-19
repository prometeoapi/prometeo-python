from typing import List, Optional
from pydantic import BaseModel


class CreatePaymentIntentResponse(BaseModel):
    intent_id: str
    external_id: Optional[str]
    concept: str
    currency: str
    amount: str
    email: Optional[str]
    bank_codes: List[str]


class StatusHistory(BaseModel):
    status: str
    message: Optional[str]
    error_type: Optional[str]
    error_code: Optional[str]
    provider_code: Optional[str]
    timestamp: str


class Customer(BaseModel):
    name: str
    document_type: Optional[str]
    document_number: Optional[str]
    email: str


class PaymentIntent(BaseModel):
    intent_id: str
    product_id: str
    external_id: Optional[str]
    concept: str
    currency: str
    amount: float
    status_history: List[StatusHistory]
    customer: Optional[Customer]
    current_status: str
