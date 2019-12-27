Prometeo Python API Client [![PyPI version](https://badge.fury.io/py/prometeo.svg)](https://badge.fury.io/py/prometeo)
===============

This is the official library for the [Prometeo API](https://prometeoapi.com/)


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


## License

[The MIT License](https://bitbucket.org/qualiauy/prometeo-python/src/master/LICENSE)
