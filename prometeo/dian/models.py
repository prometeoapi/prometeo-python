from collections import namedtuple


CompanyInfo = namedtuple('CompanyInfo', [
    'accountant',
    'capital_composition',
    'reason',
    'pdf_url',
    'pdf',
    'location',
    'name',
    'constitution_date',
    'representation',
    'members',
])

Accountant = namedtuple('Accountant', [
    'document',
    'start_date',
    'name',
    'professional_card',
])

CapitalComposition = namedtuple('CapitalComposition', [
    'national',
    'national_private',
    'national_public',
    'foreign',
    'foreign_private',
    'foreign_public',
])

Location = namedtuple('Location', [
    'country',
    'city',
    'phone1',
    'phone2',
    'department',
    'address',
    'email',
])

Representative = namedtuple('Representative', [
    'document',
    'document_type',
    'name',
    'representation_type',
    'start_date',
])

Member = namedtuple('Member', [
    'document_type',
    'document',
    'nationality',
    'name',
    'start_date'
])

Name = namedtuple('Name', [
    'first_surname',
    'second_surname',
    'first_name',
    'other_names'
])

Balance = namedtuple('Balance', [
    'type',
    'amount',
    'value'
])

RentDeclaration = namedtuple('RentDeclaration', [
    'pdf_url',
    'pdf',
    'fields',
    'year',
    'form_number',
    'nit',
    'dv',
    'name',
    'reason',
    'direction_code',
    'economic_activity',
    'correction_code',
    'previous_form'
])

Field = namedtuple('Field', [
    'name',
    'number',
    'value'
])

VATDeclaration = namedtuple('VATDeclaration', [
    'pdf_url',
    'pdf',
    'fields',
    'year',
    'period',
    'form_number',
    'nit',
    'dv',
    'name',
    'reason',
    'direction_code',
    'correction_code',
    'previous_form'
])

Numeration = namedtuple('Numeration', [
    'nit',
    'dv',
    'name',
    'reason',
    'address',
    'country',
    'department',
    'municipality',
    'ranges',
    'pdf_url',
    'pdf_available'
])

NumerationRange = namedtuple('Range', [
    'from_number',
    'to_number',
    'mode',
    'establishment',
    'prefix',
    'type'
])

Retentions = namedtuple('Retentions', [
    'pdf_url',
    'pdf',
    'fields',
    'year',
    'period',
    'form_number',
    'nit',
    'reason',
    'direction_code'
])
