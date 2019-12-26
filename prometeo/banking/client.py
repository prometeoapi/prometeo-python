from datetime import datetime

from prometeo import exceptions, base_client
from .models import (
    Client as Client, Account as AccountModel, Movement, CreditCard as CreditCardModel,
    Provider, ProviderDetail,
)


TESTING_URL = 'https://test.prometeo.qualia.uy'
PRODUCTION_URL = 'https://prometeo.qualia.uy'


class BankingAPIClient(base_client.BaseClient):

    ENVIRONMENTS = {
        'testing': TESTING_URL,
        'production': PRODUCTION_URL,
    }

    def login(self, provider, username, password):
        response = self.call_api('POST', '/login/', data={
            'provider': provider,
            'username': username,
            'password': password,
        })
        if response['status'] in ['logged_in', 'select_client']:
            return Session(self, response['status'], response['key'])
        elif response['status'] == 'interaction_required':
            return Session(
                self, response['status'], response['key'],
                response['context'], response['field'],
            )
        elif response['status'] == 'wrong_credentials':
            raise exceptions.WrongCredentialsError(response['message'])
        else:
            raise exceptions.BankingClientError(response['message'])

    def get_clients(self, session_key):
        response = self.call_api('GET', '/client/', params={
            'key': session_key,
        })
        clients = []
        for id, name in response['clients'].items():
            clients.append(Client(id=id, name=name))
        return clients

    def select_client(self, session_key, client_id):
        self.call_api('GET', '/client/{}/'.format(client_id), params={
            'key': session_key,
        })

    def get_accounts(self, session_key):
        data = self.call_api('GET', '/account/', params={
            'key': session_key,
        })
        return [
            AccountModel(**account) for account in data['accounts']
        ]

    def get_movements(
            self, session_key, account_number, currency_code, date_start, date_end
    ):
        data = self.call_api('GET', '/movement/', params={
            'key': session_key,
            'account': account_number,
            'currency': currency_code,
            'date_start': date_start.strftime('%d/%m/%Y'),
            'date_end': date_end.strftime('%d/%m/%Y'),
        })
        return [
            Movement(
                id=movement['id'],
                reference=movement['reference'],
                date=datetime.strptime(movement['date'], "%d/%m/%Y"),
                detail=movement['detail'],
                debit=movement['debit'],
                credit=movement['credit'],
            )
            for movement in data['movements']
        ]

    def get_credit_cards(self, session_key):
        data = self.call_api('GET', '/credit-card/', params={
            'key': session_key,
        })
        return [
            CreditCardModel(
                id=credit_card['id'],
                name=credit_card['name'],
                number=credit_card['number'],
                close_date=datetime.strptime(credit_card['close_date'], "%d/%m/%Y"),
                due_date=datetime.strptime(credit_card['due_date'], "%d/%m/%Y"),
                balance_local=credit_card['balance_local'],
                balance_dollar=credit_card['balance_dollar'],
            )
            for credit_card in data['credit_cards']
        ]

    def get_credit_card_movements(
            self, session_key, card_number, currency_code, date_start, date_end
    ):
        url = '/credit-card/{}/movements'.format(card_number)
        data = self.call_api('GET', url, params={
            'key': session_key,
            'currency': currency_code,
            'date_start': date_start.strftime('%d/%m/%Y'),
            'date_end': date_end.strftime('%d/%m/%Y'),
        })
        return [
            Movement(
                id=movement['id'],
                reference=movement['reference'],
                date=datetime.strptime(movement['date'], "%d/%m/%Y"),
                detail=movement['detail'],
                debit=movement['debit'],
                credit=movement['credit'],
            )
            for movement in data['movements']
        ]

    def get_providers(self):
        data = self.call_api('GET', '/provider/')
        return [
            Provider(**provider) for provider in data['providers']
        ]

    def get_provider_detail(self, provider_code):
        data = self.call_api('GET', '/provider/{}/'.format(provider_code))
        return ProviderDetail(**data['provider'])


class Session(object):

    def __init__(self, client, status, session_key, context=None, field=None):
        self._client = client
        self._status = status
        self._session_key = session_key
        self._interactive_context = context
        self._interactive_field = field

    def get_status(self):
        return self._status

    def get_session_key(self):
        return self._session_key

    def get_clients(self):
        return self._client.get_clients(self._session_key)

    def select_client(self, client):
        self._client.select_client(self._session_key, client.id)

    def get_accounts(self):
        accounts_data = self._client.get_accounts(self._session_key)
        accounts = []
        for account_data in accounts_data:
            accounts.append(Account(
                self._client, self._session_key, account_data,
            ))
        return accounts

    def get_credit_cards(self):
        cards_data = self._client.get_credit_cards(self._session_key)
        cards = []
        for card_data in cards_data:
            cards.append(CreditCard(
                self._client, self._session_key, card_data,
            ))
        return cards

    def get_interactive_context(self):
        return self._interactive_context

    def finish_login(self, provider, username, password, answer):
        self._client.call_api('POST', '/login/', data={
            'provider': provider,
            'username': username,
            'password': password,
            self._interactive_field: answer,
        })


class Account(object):

    def __init__(self, client, session_key, account_data):
        self._client = client
        self._session_key = session_key

        self.id = account_data.id
        self.name = account_data.name
        self.number = account_data.number
        self.branch = account_data.branch
        self.currency = account_data.currency
        self.balance = account_data.balance

    def get_movements(self, date_start, date_end):
        return self._client.get_movements(
            self._session_key, self.number, self.currency, date_start, date_end,
        )


class CreditCard(object):
    def __init__(self, client, session_key, card_data):
        self._client = client
        self._session_key = session_key

        self.id = card_data.id
        self.name = card_data.name
        self.number = card_data.number
        self.close_data = card_data.close_date
        self.due_date = card_data.due_date
        self.balance_local = card_data.balance_local
        self.balance_dollar = card_data.balance_dollar

    def get_movements(self, currency_code, date_start, date_end):
        return self._client.get_credit_card_movements(
            self._session_key, self.number, currency_code, date_start, date_end,
        )
