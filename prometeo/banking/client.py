from datetime import datetime

from prometeo import exceptions, base_client, base_session
from .models import (
    Client as Client, Account as AccountModel, Movement, CreditCard as CreditCardModel,
    Provider, ProviderDetail, PreprocessTransfer, ConfirmTransfer, TransferInstitution
)
from .exceptions import BankingClientError


TESTING_URL = 'https://test.prometeo.qualia.uy'
PRODUCTION_URL = 'https://prometeo.qualia.uy'


class Session(base_session.BaseSession):
    """
    Encapsulates the user's session, returned by
    :meth:`~prometeo.banking.client.BankingAPIClient.login`
    """

    def __init__(self, client, status, session_key, context=None, field=None):
        super(Session, self).__init__(client, status, session_key)
        self._interactive_context = context
        self._interactive_field = field

    def get_clients(self):
        """
        List the user's clients. Returns an empty list if the bank doesn't uses clients.

        :rtype: List of :class:`~prometeo.banking.models.Client`
        """
        return self._client.get_clients(self._session_key)

    def select_client(self, client):
        """
        Selects the client to use for this session.

        :param client_id: The id of the client, obtained from listing the clients
        :type client_id: str
        """
        self._client.select_client(self._session_key, client.id)

    def get_accounts(self):
        """
        List all the user's accounts

        :rtype: List of :class:`~prometeo.banking.models.Account`
        """
        accounts_data = self._client.get_accounts(self._session_key)
        accounts = []
        for account_data in accounts_data:
            accounts.append(Account(
                self._client, self._session_key, account_data,
            ))
        return accounts

    def get_credit_cards(self):
        """
        List all the user's credit cards

        :rtype: List of :class:`~prometeo.banking.models.CreditCard`
        """
        cards_data = self._client.get_credit_cards(self._session_key)
        cards = []
        for card_data in cards_data:
            cards.append(CreditCard(
                self._client, self._session_key, card_data,
            ))
        return cards

    def get_interactive_context(self):
        """
        Necessary information to answer the login challenge, like a security question.

        :rtype: str
        """
        return self._interactive_context

    def finish_login(self, provider, username, password, answer):
        """
        Answer the security challenge, like an OTP or personal question.

        :param provider: The provider used to login
        :type provider: str

        :param username: The username used to login
        :type username: str

        :param password: The password used to login
        :type password: str

        :param answer: The answer to the login challenge
        :type answer: str
        """
        self._client.call_api('POST', '/login/', data={
            'provider': provider,
            'username': username,
            'password': password,
            self._interactive_field: answer,
        }, params={
            'key': self._session_key,
        })

    def logout(self):
        """
        Logs the user out and invalidates its session.
        """
        self._client.logout(self._session_key)

    def preprocess_transfer(self, origin_account, destination_institution,
                            destination_account, currency, amount, concept,
                            destination_owner_name, branch):
        """
        Preprocess transfer.

        :param origin_account: Account number from where it is transferred
        :type origin_account: str

        :param destination_institution: Id of the institution where it is transferred.
                                        As provided by
                                        :meth:`~prometeo.banking.client.BankingAPIClient.get_providers`
        :type destination_institution: str

        :param destination_account: Account number where it is transferred
        :type destination_account: str

        :param currency: Account currency in format ``ISO 4217``
        :type currency: str

        :param amount: Amount to transfer
        :type amount: str

        :param concept: Concept or description of the transfer
        :type concept: str

        :param destination_owner_name:
            Name of the holder of the destination account (empty if not applicable)
        :type destination_owner_name: str

        :param branch: Branch number of the destination account
                       (empty if not applicable)
        :type branch: str

        :rtype: :class:`~prometeo.banking.models.PreprocessTransfer`
        """
        return self._client.preprocess_transfer(self._session_key, origin_account,
                                                destination_institution,
                                                destination_account, currency, amount,
                                                concept, destination_owner_name, branch)

    def confirm_transfer(self, request_id, authorization_type, authorization_data):
        """
        Confirm transfer.

        :param request_id: Id of the request returned by the endpoint of
                           :meth:`~prometeo.banking.client.BankingAPIClient.preprocess_transfer`
        :type request_id: str

        :param authorization_type:
            - ``cardCode`` Coordinates card
            - ``pin`` Account personal pin
            -
                ``otp`` One-time generated pin, sent by sms, email,
                hard token or soft token.
            - ``otp-api`` Hard token or soft token device, digitized by Promete

        :type authorization_type: str

        :param authorization_data: Verification value (pin number,
                                   coordinates card response , etc) if there
                                   are several values, they must be separated by commas.
        :type authorization_data: str

        :rtype: :class:`~prometeo.banking.models.ConfirmTransfer`
        """
        return self._client.confirm_transfer(self._session_key, request_id,
                                             authorization_type, authorization_data)

    def list_transfer_institutions(self):
        """
        List transfer institutions.

        :rtype: :class:`~prometeo.banking.models.TransferInstitution`
        """
        return self._client.list_transfer_institutions(self._session_key)


class BankingAPIClient(base_client.BaseClient):
    """
    API Client for banking api
    """

    ENVIRONMENTS = {
        'testing': TESTING_URL,
        'production': PRODUCTION_URL,
    }

    session_class = Session

    def on_response(self, data):
        if data['status'] == 'error':
            if data['message'] == 'Invalid key':
                raise exceptions.InvalidSessionKeyError(data['message'])
            else:
                raise BankingClientError(data['message'])

    def login(self, provider, username, password, **kwargs):
        """
        Start log in process with the provider

        :param provider: Name of the provider,
                         use :meth:`~BankingAPIClient.get_providers`
                         to get a list of available providers
        :type provider: str

        :param username: Username used to log in to the banking app or web
        :type username: str

        :param password: User's password
        :type password: str

        :param kwargs: Extra login fields for providers that require it,
                       use :meth:`~BankingAPIClient.get_provider_detail`
                       to get a list of all the auth login fields
        :type kwargs: dict

        :rtype: :class:`~prometeo.banking.client.Session`
        """
        data = {
            'provider': provider,
            'username': username,
            'password': password,
        }
        data.update(kwargs)
        response = self.call_api('POST', '/login/', data=data)
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
            raise BankingClientError(response['message'])

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
        """
        List all available banks.

        :rtype: :class:`~prometeo.banking.models.Provider`
        """
        data = self.call_api('GET', '/provider/')
        return [
            Provider(**provider) for provider in data['providers']
        ]

    def get_provider_detail(self, provider_code):
        """
        Get more detailed information about a bank.

        :param provider_code: Name of the provider, as returned in
                              :meth:`~prometeo.banking.client.BankingAPIClient.get_providers`
        :type provider_code: str

        :rtype: :class:`~prometeo.banking.models.ProviderDetail`
        """
        data = self.call_api('GET', '/provider/{}/'.format(provider_code))
        return ProviderDetail(**data['provider'])

    def logout(self, session_key):
        """
        Logs the user out and invalidates its session.

        :param session_key: The session key.
        :type session_key: str
        """
        self.call_api('GET', '/logout/', params={
            'key': session_key,
        })

    def preprocess_transfer(self, session_key, origin_account,
                            destination_institution, destination_account, currency,
                            amount, concept, destination_owner_name, branch):
        """
        Preprocess transfer.

        :param session_key: The session key.
        :type session_key: str

        :param origin_account: Account number from where it is transferred
        :type origin_account: str

        :param destination_institution: Id of the institution where it is transferred.
                                        As provided by
                                        :meth:`~prometeo.banking.client.BankingAPIClient.get_providers`
        :type destination_institution: str

        :param destination_account: Account number where it is transferred
        :type destination_account: str

        :param currency: Account currency in format ``ISO 4217``
        :type currency: str

        :param amount: Amount to transfer
        :type amount: str

        :param concept: Concept or description of the transfer
        :type concept: str

        :param destination_owner_name:
            Name of the holder of the destination account (empty if not applicable)
        :type destination_owner_name: str

        :param branch:
            Branch number of the destination account (empty if not applicable)
        :type branch: str

        :rtype: :class:`~prometeo.banking.models.PreprocessTransfer`
        """
        data = self.call_api('POST', '/transfer/preprocess', params={
            'key': session_key,
        }, data={
            'origin_account': origin_account,
            'destination_institution': destination_institution,
            'destination_account': destination_account,
            'currency': currency,
            'amount': amount,
            'concept': concept,
            'destination_owner_name': destination_owner_name,
            'branch': branch,
        })
        return PreprocessTransfer(**data['result'])

    def confirm_transfer(self, session_key, request_id, authorization_type,
                         authorization_data):
        """
        Confirm transfer.

        :param session_key: The session key.
        :type session_key: str

        :param request_id: Id of the request returned by the endpoint of
                           :meth:`~prometeo.banking.client.BankingAPIClient.preprocess_transfer`
        :type request_id: str

        :param authorization_type:
            - ``cardCode`` Coordinates card
            - ``pin`` Account personal pin
            -
                ``otp`` One-time generated pin, sent by sms, email,
                hard token or soft token.
            - ``otp-api`` Hard token or soft token device, digitized by Prometeo

        :type authorization_type: str

        :param authorization_data: Verification value (pin number,
                                   coordinates card response , etc) if there
                                   are several values, they must be separated by commas.
        :type authorization_data: str

        :rtype: :class:`~prometeo.banking.models.ConfirmTransfer`
        """
        data = self.call_api('POST', '/transfer/confirm', params={
            'key': session_key,
        }, data={
            'request_id': request_id,
            'authorization_type': authorization_type,
            'authorization_data': authorization_data,
        })
        return ConfirmTransfer(**data['transfer'])

    def list_transfer_institutions(self, session_key):
        """
        List transfer institutions.

        :param session_key: The session key.
        :type session_key: str

        :rtype: :class:`~prometeo.banking.models.TransferInstitution`
        """
        data = self.call_api('GET', '/transfer/destinations', params={
            'key': session_key,
        })
        return [
            TransferInstitution(**institution) for institution in data['destinations']
        ]


class Account(object):
    """
    A bank account, returned by :meth:`~prometeo.banking.client.Session.get_accounts`
    """

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
        """
        List an account's movements for a range of dates.

        :param date_start: Start of the date range for movements.
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End of the date range for movements.
        :type date_end: :class:`~datetime.datetime`

        :rtype: List of :class:`~prometeo.banking.models.Movement`
        """
        return self._client.get_movements(
            self._session_key, self.number, self.currency, date_start, date_end,
        )


class CreditCard(object):
    """
    A credit card, returned by :meth:`~prometeo.banking.client.Session.get_credit_cards`
    """

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
        """
        List credit card's movements for a range of dates.

        :param date_start: Start of the date range for movements.
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End of the date range for movements.
        :type date_end: :class:`~datetime.datetime`

        :rtype: List of :class:`~prometeo.banking.models.Movement`
        """
        return self._client.get_credit_card_movements(
            self._session_key, self.number, currency_code, date_start, date_end,
        )
