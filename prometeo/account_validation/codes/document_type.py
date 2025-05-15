from enum import Enum

class BrazilDocument(Enum):
    CADASTRO_NACIONAL_DA_PESSOA_JURIDICA = "CNPJ"
    CADASTRO_DE_PESSOAS_FISICAS = "CPF"

class ColombiaDocument(Enum):
    CITIZENSHIP_CARD = "CC"
    TAX_IDENTIFICATION_NUMBER = "NIT"

class ChileDocument(Enum):
    SINGLE_TAX_REGISTRY = "RUT"

class EcuadorDocument(Enum):
    CITIZENSHIP_CARD = "CC"
    SINGLE_TAXPAYERS_REGISTRY = "RUC"
    PASSPORT = "PAS"

class MexicoDocument(Enum):
    FEDERAL_TAXPAYER_REGISTRATION = "RFC"

class PeruDocument(Enum):
    NATIONAL_IDENTITY_DOCUMENT = "DNI"
    SINGLE_TAXPAYER_REGISTRY = "RUC"

class UruguayDocument(Enum):
    WRIT_IDENTITY = "CI"
    SINGLE_TAX_REGISTRY = "RUT"
