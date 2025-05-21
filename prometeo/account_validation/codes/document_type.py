from enum import Enum


def extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)

    return wrapper


class DocumentType(Enum):
    pass


@extend_enum(DocumentType)
class BrazilDocument(Enum):
    CADASTRO_NACIONAL_DA_PESSOA_JURIDICA = "CNPJ"
    CADASTRO_DE_PESSOAS_FISICAS = "CPF"


@extend_enum(DocumentType)
class ColombiaDocument(Enum):
    CITIZENSHIP_CARD = "CC"
    TAX_IDENTIFICATION_NUMBER = "NIT"


@extend_enum(DocumentType)
class ChileDocument(Enum):
    SINGLE_TAX_REGISTRY = "RUT"


@extend_enum(DocumentType)
class EcuadorDocument(Enum):
    CITIZENSHIP_CARD = "CC"
    SINGLE_TAXPAYERS_REGISTRY = "RUC"
    PASSPORT = "PAS"


@extend_enum(DocumentType)
class MexicoDocument(Enum):
    FEDERAL_TAXPAYER_REGISTRATION = "RFC"


@extend_enum(DocumentType)
class PeruDocument(Enum):
    NATIONAL_IDENTITY_DOCUMENT = "DNI"
    SINGLE_TAXPAYER_REGISTRY = "RUC"


@extend_enum(DocumentType)
class UruguayDocument(Enum):
    WRIT_IDENTITY = "CI"
    SINGLE_TAX_REGISTRY = "RUT"
