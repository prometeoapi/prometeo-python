from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Balance(BaseModel):
    type: str
    amount: float
    value: float


class Name(BaseModel):
    first_surname: str
    second_surname: str
    first_name: str
    other_names: str


class Field(BaseModel):
    name: str
    number: int
    value: float


class NumerationRange(BaseModel):
    from_number: int
    to_number: int
    mode: str
    establishment: str
    prefix: str
    type: str


class Numeration(BaseModel):
    nit: Optional[str]
    dv: Optional[str]
    name: Optional[Name]
    reason: Optional[str]
    address: Optional[str]
    country: Optional[str]
    department: Optional[str]
    municipality: Optional[str]
    ranges: List[NumerationRange]
    pdf_url: Optional[str]
    pdf_available: Optional[bool]


class RentDeclaration(BaseModel):
    pdf_url: Optional[str]
    pdf: Optional[object]
    fields: List[Field]
    year: int
    form_number: int
    nit: str
    dv: str
    name: Name
    reason: str
    direction_code: str
    economic_activity: str
    correction_code: str
    previous_form: Optional[str]


class VATDeclaration(BaseModel):
    pdf_url: Optional[str]
    pdf: Optional[object]
    fields: List[Field]
    year: int
    period: str
    form_number: int
    nit: str
    dv: str
    name: Name
    reason: str
    direction_code: str
    correction_code: str
    previous_form: Optional[str]


class Retentions(BaseModel):
    pdf_url: Optional[str]
    pdf: Optional[object]
    fields: List[Field]
    year: int
    period: int
    form_number: int
    nit: str
    reason: str
    direction_code: str


class Representative(BaseModel):
    document: str
    document_type: str
    name: Name
    representation_type: str
    start_date: datetime


class Member(BaseModel):
    document_type: str
    document: str
    nationality: str
    name: Name
    start_date: datetime


class Location(BaseModel):
    country: str
    city: str
    phone1: str
    phone2: str
    department: str
    address: str
    email: str


class CapitalComposition(BaseModel):
    national: str
    national_private: str
    national_public: str
    foreign: str
    foreign_private: str
    foreign_public: str


class Accountant(BaseModel):
    document: str
    start_date: datetime
    name: str
    professional_card: str


class CompanyInfo(BaseModel):
    accountant: Accountant
    capital_composition: CapitalComposition
    reason: str
    pdf_url: Optional[str]
    pdf: Optional[object]
    location: Location
    name: str
    constitution_date: datetime
    representation: List[Representative]
    members: List[Member]

    class Config:
        validate_assignment = True
