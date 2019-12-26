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
    'credit'
])

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
