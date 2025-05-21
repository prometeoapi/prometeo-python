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


class AccountType(Enum):
    CUENTA_CORRIENTE = "CHECKING"
    CUENTA_AHORRO = "SAVINGS"


@extend_enum(AccountType)
class AccountTypeBrasil(Enum):
    CONTA_FACIL = "EASY"
    CONTA_PAGAMENTO = "PAYMENTS"
    ENTIDADES_PUBLICAS = "PUBLIC_ENTITY"
    PIX_KEY = "PIX_KEY"


@extend_enum(AccountType)
class AccountTypeChile(Enum):
    CUENTA_EFECTIVO = "DEMAND"


@extend_enum(AccountType)
class AccountTypeEcuador(Enum):
    VIRTUAL_ACCOUNT = "VIRTUAL_ACCOUNT"
    ELECTRONIC_ROLE_ACCOUNT = "ROL_ELECTRONICO"
    FRIEND_ACCOUNT = "CUENTA_AMIGA"
    DEBIT_CARD = "CARD"
