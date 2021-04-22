from collections import namedtuple

Client = namedtuple('Client', [
    'id',
    'name',
])


Account = namedtuple('Account', [
    'id',
    'name',
    'number',
    'branch',
    'currency',
    'balance',
])

CreditCard = namedtuple('CreditCard', [
    'id',
    'name',
    'number',
    'close_date',
    'due_date',
    'balance_local',
    'balance_dollar',
])

Movement = namedtuple('Movement', [
    'id',
    'reference',
    'date',
    'detail',
    'debit',
    'credit',
    'extra_data',
])
Movement.__new__.__defaults__ = (None,)

Provider = namedtuple('Provider', [
    'code',
    'country',
    'name',
])

ProviderDetail = namedtuple('ProviderDetail', [
    'country',
    'name',
    'auth_fields',
])

PreprocessTransfer = namedtuple('PreprocessTransfer', [
    'approved',
    'authorization_devices',
    'message',
    'request_id',
])

ConfirmTransfer = namedtuple('ConfirmTransfer', [
    'message',
    'success',
])

TransferInstitution = namedtuple('TransferInstitution', [
    'id',
    'name',
])
