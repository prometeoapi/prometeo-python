Prometeo Python API Client [![PyPI version](https://badge.fury.io/py/prometeo.svg)](https://badge.fury.io/py/prometeo) [![Documentation Status](https://readthedocs.org/projects/prometeo-python/badge/?version=latest)](https://prometeo-python.readthedocs.io/en/latest/?badge=latest) ![Bitbucket Pipelines branch](https://img.shields.io/bitbucket/pipelines/qualiauy/prometeo-python/master)
===============

This is the official python library for the [Prometeo API](https://prometeoapi.com/)

## Documentation

Complete client documentation is available at [Read the docs](https://readthedocs.org/projects/prometeo-python/)

## Installation

### Prerequisites

* Python version 2.7 and 3.5+
* An API Key ([contact us](mailto:info@prometeoapi.com) to get one!)

### Install package

```console
$ pip install prometeo
```


## Quick Start

### Get your key

Go to [your dashboard](https://test.prometeo.qualia.uy/dashboard/), there you'll find your API key. Use it to instantiate the client:

```python
from prometeo import Client


client = Client('<YOUR_API_KEY>', environment='testing')
```

The `environment` argument is either `testing` for the sandbox or `production` for the production environment.

### Listing movements

The following example logs in to the sandboxed bank and retrieves a list of movements

```python
from datetime import datetime

session = client.banking.login(provider='test', username='12345', password='gfdsa')
accounts = session.get_accounts()
account = accounts[0]
print(account.number, ' - ', account.name)
movements = account.get_movements(datetime(2019, 2, 1), datetime(2019, 2, 2))
for movement in movements:
    print(movement.detail, movement.debit, movement.credit)
```

### Listing credit card movements

```python
cards = session.get_credit_cards()
card = cards[0]
print(card.number, ' - ', card.name)
movements = card.get_movements('USD', datetime(2019, 2, 1), datetime(2019, 2, 2))
for movement in movements:
    print(movement.detail, movement.debit, movement.credit)
```

### Listing all available banks

```python
providers = client.banking.get_providers()
for provider in providers:
    print(provider.name, provider.country)
```


## CURP API

### Checking the existence of a curp

```python
from prometeo.curp import exceptions

curp = 'ABCD12345EFGH'
try:
    result = client.curp.query(curp)
except exceptions.CurpError as e:
    print("CURP does not exist:", e.message)
```

### Looking for a CURP by person

```python
from datetime import datetime
from prometeo.curp import exceptions, Gender, State

curp = 'ABCD12345EFGH'
state = State.SINALOA
birthdate = datetime(1988, 3, 4)
name = 'JOHN'
first_surname = 'DOE'
last_surname = 'PONCE'
gender = Gender.MALE
try:
    result = client.curp.reverse_query(
        state, birthdate, name, first_surname, last_surname, gender
    )
except exceptions.CurpError as e:
    print("CURP does not exist:", e.message)
```


## DIAN API

### Log in

Supply the NIT to log in as a company:

```python
from prometeo.dian import DocumentType

session = client.dian.login(
    nit='098765',
    document_type=DocumentType.CEDULA_CIUDADANIA,
    document='12345',
    password='test_password',
)
```

Or omit it to log in as a person:

```python
from prometeo.dian import DocumentType

session = client.dian.login(
    document_type=DocumentType.CEDULA_CIUDADANIA,
    document='12345',
    password='test_password',
)
```

### Get the data

Company info:

```python
session.get_company_info()
```

Balances:

```python
session.get_balances()
```

Rent declaration:

```python
session.get_rent_declaration(2018)
```

VAT declaration:

```python
from prometeo.dian import Periodicity, QuartlerlyPeriod

session.get_vat_declaration(2019, Periodicity.QUARTERLY, QuartlerlyPeriod.JANUARY_APRIL)
```

Numeration:

```python
from datetime import datetime
from prometeo.dian import NumerationType

session.get_numeration(NumerationType.Authorization, datetime(2019, 1, 1), datetime(2019, 5, 1))
```

Retentions:

```python
from prometeo.dian import MonthlyPeriod

session.get_retentions(2019, MonthlyPeriod.NOVEMBER)
```

## SAT API

### Login in

```python
from prometeo.sat import LoginScope

session = client.sat.login(
    rfc='ABCD1234EFGH',
    password='password',
    scope=LoginScope.CFDI,
)
```

### Work with CFDI bills

List emitted and received bills

```python
from prometeo.sat import BillStatus

emitted_bills = session.get_emitted_bills(
    date_start=datetime(2020, 1, 1),
    date_end=datetime(2020, 2, 1),
    status=BillStatus.ANY,
)

received_bills = session.get_received_bills(
    year=2020,
    month=1,
    status=BillStatus.ANY,
```

Bulk download of bills

```python
from prometeo.sat import BillStatus

download_requests = session.download_emitted_bills(
    date_start=datetime(2020, 1, 1),
    date_end=datetime(2020, 2, 1),
    status=BillStatus.ANY,
)
for request in download_requests:
    download = request.get_download()
    content = download.get_file().read()
```

Download acknowledgements

```python
from prometeo.sat import Motive, DocumentType, Status, SendType

acks = session.get_acknowledgement(
    year=2020,
    month_start=1,
    month_end=2,
    motive=Motive.ALL,
    document_type=DocumentType.ALL,
    status=Status.ALL,
    send_type=SendType.ALL,
)
for ack in acks:
    download = ack.download().get_file()
```

## License

[The MIT License](https://bitbucket.org/qualiauy/prometeo-python/src/master/LICENSE)
