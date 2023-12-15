from datetime import datetime

from prometeo import exceptions, base_client, base_session, utils
from .models import (
    Client as Client,
    Account as AccountModel,
    Movement,
    CreditCard as CreditCardModel,
    Provider,
    ProviderDetail,
    PreprocessTransfer,
    ConfirmTransfer,
    TransferInstitution,
)
from .exceptions import BankingClientError


PRODUCTION_URL = "https://banking.prometeoapi.net"
SANDBOX_URL = "https://banking.sandbox.prometeoapi.com"


class Session(base_session.BaseSession):
    """
    Encapsulates the user's session, returned by
    :meth:`~prometeo.banking.client.BankingAPIClient.login`
    """

    def __init__(self, client, status, session_key, context=None, field=None):
        super(Session, self).__init__(client, status, session_key)
        self._interactive_context = context
        self._interactive_field = field

    @utils.adapt_async_sync
    async def login(self, provider, username, password, **kwargs):
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
            "provider": provider,
            "username": username,
            "password": password,
            **kwargs,
        }
        response = await self._client.login(**data)
        if response["status"] in ["logged_in", "select_client"]:
            self._session_key = response.get("key") or self._session_key
            self._status = response["status"]
        elif response["status"] == "interaction_required":
            self._session_key = response.get("key")
            self._status = response["status"]
            self._interactive_context = response["context"]
            self._interactive_field = response["field"]
        elif response["status"] == "wrong_credentials":
            raise exceptions.WrongCredentialsError(response["message"])
        else:
            raise BankingClientError(response["message"])

    @utils.adapt_async_sync
    async def finish_login(self, provider, username, password, answer):
        return await self.login(
            provider,
            username,
            password,
            session_key=self._session_key,
            **{self._interactive_field: answer},
        )

    @utils.adapt_async_sync
    async def get_clients(self):
        """
        List the user's clients. Returns an empty list if the bank doesn't uses clients.

        :rtype: List of :class:`~prometeo.banking.models.Client`
        """
        response = await self._client.get_clients(self._session_key)
        clients = []
        for id, name in response["clients"].items():
            clients.append(Client(id=id, name=name))
        return clients

    @utils.adapt_async_sync
    async def select_client(self, client):
        """
        Selects the client to use for this session.

        :param client_id: The id of the client, obtained from listing the clients
        :type client_id: str
        """
        await self._client.select_client(self._session_key, client.id)

    @utils.adapt_async_sync
    async def get_accounts(self):
        """
        List all the user's accounts

        :rtype: List of :class:`~prometeo.banking.models.Account`
        """
        data = await self._client.get_accounts(self._session_key)
        accounts_data = [AccountModel(**account) for account in data["accounts"]]
        accounts = []
        for account_data in accounts_data:
            accounts.append(
                Account(
                    self._client,
                    self._session_key,
                    account_data,
                )
            )
        return accounts

    @utils.adapt_async_sync
    async def get_credit_cards(self):
        """
        List all the user's credit cards

        :rtype: List of :class:`~prometeo.banking.models.CreditCard`
        """
        data = await self._client.get_credit_cards(self._session_key)
        cards_data = [
            CreditCardModel(
                id=credit_card["id"],
                name=credit_card["name"],
                number=credit_card["number"],
                close_date=datetime.strptime(credit_card["close_date"], "%d/%m/%Y"),
                due_date=datetime.strptime(credit_card["due_date"], "%d/%m/%Y"),
                balance_local=credit_card["balance_local"],
                balance_dollar=credit_card["balance_dollar"],
            )
            for credit_card in data["credit_cards"]
        ]
        cards = []
        for card_data in cards_data:
            cards.append(
                CreditCard(
                    self._client,
                    self._session_key,
                    card_data,
                )
            )
        return cards

    @utils.adapt_async_sync
    def get_interactive_context(self):
        """
        Necessary information to answer the login challenge, like a security question.

        :rtype: str
        """
        return self._interactive_context

    @utils.adapt_async_sync
    async def get_providers(self):
        """
        List all available banks.

        :rtype: :class:`~prometeo.banking.models.Provider`
        """
        data = await self._client.get_providers()
        return [Provider(**provider) for provider in data["providers"]]

    @utils.adapt_async_sync
    async def get_provider_detail(self, provider_code, key=None, value=None):
        """
        Get more detailed information about a bank.

        :param provider_code: Name of the provider, as returned in
                              :meth:`~prometeo.banking.client.BankingAPIClient.get_providers`
        :type provider_code: str

        :param key: Auth Field Key (for filtering options)
        :type key: str

        :param value: Auth Field Value (for filtering options)
        :type value: str

        :rtype: :class:`~prometeo.banking.models.ProviderDetail`
        """
        data = await self._client.get_provider_detail(provider_code, key, value)
        return ProviderDetail(**data["provider"])

    @utils.adapt_async_sync
    async def logout(self):
        """
        Logs the user out and invalidates its session.
        """
        await self._client.logout(self._session_key)

    @utils.adapt_async_sync
    async def preprocess_transfer(
        self,
        origin_account,
        destination_institution,
        destination_account,
        currency,
        amount,
        concept,
        destination_owner_name,
        branch,
        destination_account_type=None,
        document_type=None,
        document_number=None,
        country=None,
        destination_bank_code=None,
        payment_intent_id=None,
        external_id=None,
        mobile_os=None,
    ):
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

        :param destination_account_type: Type of the destination account (optional)
        :type destination_account_type: str

        :param document_type: Document type (optional)
        :type document_type: str

        :param document_number: Document number (optional)
        :type document_number: str

        :param country: Country (optional)
        :type country: str

        :param destination_bank_code: Bank code of the destination (optional)
        :type destination_bank_code: str

        :param payment_intent_id: Payment intent ID (optional)
        :type payment_intent_id: str

        :param external_id: External ID (optional)
        :type external_id: str

        :param mobile_os: Mobile OS (optional)
        :type mobile_os: str

        :rtype: :class:`~prometeo.banking.models.PreprocessTransfer`
        """
        data = await self._client.preprocess_transfer(
            self._session_key,
            origin_account,
            destination_institution,
            destination_account,
            currency,
            amount,
            concept,
            destination_owner_name,
            branch,
        )
        return PreprocessTransfer(**data["result"])

    @utils.adapt_async_sync
    async def confirm_transfer(
        self,
        request_id,
        authorization_type,
        authorization_data,
        authorization_device_number=None,
    ):
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

        :param authorization_device_number: OTP Device Serial Number
        :type authorization_device_number: str

        :rtype: :class:`~prometeo.banking.models.ConfirmTransfer`
        """
        data = await self._client.confirm_transfer(
            self._session_key,
            request_id,
            authorization_type,
            authorization_data,
            authorization_device_number,
        )
        return ConfirmTransfer(**data["transfer"])

    @utils.adapt_async_sync
    async def list_transfer_institutions(self):
        """
        List transfer institutions.

        :rtype: :class:`~prometeo.banking.models.TransferInstitution`
        """
        data = await self._client.list_transfer_institutions(self._session_key)
        return [
            TransferInstitution(**institution) for institution in data["destinations"]
        ]


class BankingAPIClient(base_client.BaseClient):
    """
    API Client for banking api
    """

    ENVIRONMENTS = {
        "production": PRODUCTION_URL,
        "sandbox": SANDBOX_URL,
    }

    session_class = Session

    def on_response(self, data):
        if data["status"] == "error":
            if data["message"] == "Invalid key":
                raise exceptions.InvalidSessionKeyError(data["message"])
            else:
                raise BankingClientError(data["message"])

    @utils.adapt_async_sync
    async def login(self, provider, username, password, session_key=None, **kwargs):
        headers = {"X-Session-Key": session_key} if session_key else {}
        return await self.call_api(
            "POST",
            "/login/",
            data={
                "provider": provider,
                "username": username,
                "password": password,
                **kwargs,
            },
            headers=headers,
        )

    @utils.adapt_async_sync
    async def login_procedure(self, session_key, **kwargs):
        return await self.call_api(
            "POST",
            "/login-procedure/",
            data={
                **kwargs,
            },
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def get_owner_info(self, session_key):
        return await self.call_api(
            "GET",
            "/info/",
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def get_transfer_authorization_methods(self, session_key):
        return await self.call_api(
            "GET",
            "/transfer/mfa-methods",
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def get_clients(self, session_key):
        return await self.call_api(
            "GET",
            "/client/",
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def select_client(self, session_key, client_id):
        return await self.call_api(
            "GET",
            "/client/{}/".format(client_id),
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def get_accounts(self, session_key):
        return await self.call_api(
            "GET",
            "/account/",
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def get_movements(
        self, session_key, account_number, currency_code, date_start, date_end
    ):
        return await self.call_api(
            "GET",
            "/movement/",
            headers={"X-Session-Key": session_key},
            params={
                "account": account_number,
                "currency": currency_code,
                "date_start": date_start.strftime("%d/%m/%Y"),
                "date_end": date_end.strftime("%d/%m/%Y"),
            },
        )

    @utils.adapt_async_sync
    async def get_credit_cards(self, session_key):
        return await self.call_api(
            "GET",
            "/credit-card/",
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def get_credit_card_movements(
        self, session_key, card_number, currency_code, date_start, date_end
    ):
        return await self.call_api(
            "GET",
            f"/credit-card/{card_number}/movements",
            headers={"X-Session-Key": session_key},
            params={
                "currency": currency_code,
                "date_start": date_start.strftime("%d/%m/%Y"),
                "date_end": date_end.strftime("%d/%m/%Y"),
            },
        )

    @utils.adapt_async_sync
    async def get_providers(self):
        return await self.call_api("GET", "/provider/")

    @utils.adapt_async_sync
    async def get_provider_detail(self, provider_code, key=None, value=None):
        params = {"key": key, "value": value} if key and value else None
        return await self.call_api("GET", f"/provider/{provider_code}/", params=params)

    @utils.adapt_async_sync
    async def logout(self, session_key):
        return await self.call_api(
            "GET",
            "/logout/",
            headers={"X-Session-Key": session_key},
        )

    @utils.adapt_async_sync
    async def preprocess_transfer(
        self,
        session_key,
        origin_account,
        destination_institution,
        destination_account,
        currency,
        amount,
        concept,
        destination_owner_name,
        branch,
        destination_account_type=None,
        document_type=None,
        document_number=None,
        country=None,
        destination_bank_code=None,
        payment_intent_id="",
        external_id=None,
        mobile_os=None,
        **kwargs,
    ):
        return await self.call_api(
            "POST",
            "/transfer/preprocess",
            headers={
                "X-Session-Key": session_key,
                "Payment-Intent-ID": payment_intent_id,
            },
            data={
                "origin_account": origin_account,
                "destination_institution": destination_institution,
                "destination_account": destination_account,
                "currency": currency,
                "amount": amount,
                "concept": concept,
                "destination_owner_name": destination_owner_name,
                "branch": branch,
                "destination_account_type": destination_account_type,
                "document_type": document_type,
                "document_number": document_number,
                "country": country,
                "destination_bank_code": destination_bank_code,
                "mobile_os": mobile_os,
                "external_id": external_id,
                **kwargs,
            },
        )

    @utils.adapt_async_sync
    async def retry_preprocess_transfer(
        self,
        session_key,
        request_id,
        **kwargs,
    ):
        return await self.call_api(
            "POST",
            "/transfer/preprocess/retry",
            headers={
                "X-Session-Key": session_key,
            },
            data={
                "request_id": request_id,
                **kwargs,
            },
        )

    @utils.adapt_async_sync
    async def confirm_transfer(
        self,
        session_key,
        request_id,
        authorization_type,
        authorization_data,
        authorization_device_number=None,
    ):
        return await self.call_api(
            "POST",
            "/transfer/confirm",
            headers={"X-Session-Key": session_key},
            data={
                "request_id": request_id,
                "authorization_type": authorization_type,
                "authorization_data": authorization_data,
                "authorization_device_number": authorization_device_number,
            },
        )

    @utils.adapt_async_sync
    async def list_transfer_institutions(self, session_key):
        return await self.call_api(
            "GET",
            "/transfer/destinations",
            headers={"X-Session-Key": session_key},
        )


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

    @utils.adapt_async_sync
    async def get_movements(self, date_start, date_end):
        """
        List an account's movements for a range of dates.

        :param date_start: Start of the date range for movements.
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End of the date range for movements.
        :type date_end: :class:`~datetime.datetime`

        :rtype: List of :class:`~prometeo.banking.models.Movement`
        """
        data = await self._client.get_movements(
            self._session_key,
            self.number,
            self.currency,
            date_start,
            date_end,
        )
        return [
            Movement(
                id=movement["id"],
                reference=movement["reference"],
                date=datetime.strptime(movement["date"], "%d/%m/%Y"),
                detail=movement["detail"],
                debit=movement["debit"],
                credit=movement["credit"],
                extra_data=movement["extra_data"],
            )
            for movement in data["movements"]
        ]


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

    @utils.adapt_async_sync
    async def get_movements(self, currency_code, date_start, date_end):
        """
        List credit card's movements for a range of dates.

        :param date_start: Start of the date range for movements.
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End of the date range for movements.
        :type date_end: :class:`~datetime.datetime`

        :rtype: List of :class:`~prometeo.banking.models.Movement`
        """
        data = await self._client.get_credit_card_movements(
            self._session_key,
            self.number,
            currency_code,
            date_start,
            date_end,
        )
        return [
            Movement(
                id=movement["id"],
                reference=movement["reference"],
                date=datetime.strptime(movement["date"], "%d/%m/%Y"),
                detail=movement["detail"],
                debit=movement["debit"],
                credit=movement["credit"],
                extra_data=movement.get("extra_data"),
            )
            for movement in data["movements"]
        ]
