# -*- coding: utf-8 -*-
from datetime import datetime

from six.moves.urllib.parse import parse_qs, urlparse
import requests_mock

from prometeo import exceptions
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestClient(BaseTestCase):

    def test_login_success(self, m):
        m.post('/login/', json={
            'status': 'logged_in',
            'key': '123456',
        })
        session = self.client.banking.login(
            provider='test_provider',
            username='test_username',
            password='test_password',
        )
        self.assertEqual('logged_in', session.get_status())
        self.assertEqual('123456', session.get_session_key())

    def test_login_wrong_credentials(self, m):
        m.post('/login/', status_code=403, json={
            'status': 'wrong_credentials',
            'message': 'wrong credentials',
        })
        with self.assertRaises(exceptions.WrongCredentialsError):
            self.client.banking.login(
                provider='test_provider',
                username='test_username',
                password='test_password',
            )

    def test_login_select_client(self, m):
        history = m.request_history
        m.post('/login/', json={
            'status': 'select_client',
            'key': '123456',
        })
        m.get('/client/', json={
            "status": "success",
            "clients": {
                "0": "First Client",
                "1": "Second Client"
            },
        })
        m.get('/client/1/', json={
            "status": "success"
        })
        session = self.client.banking.login(
            provider='test_provider',
            username='test_username',
            password='test_password',
        )
        self.assertEqual('select_client', session.get_status())
        self.assertEqual('123456', session.get_session_key())

        clients = session.get_clients()
        self.assertEqual('/client/', history[-1].path)

        client = [client for client in clients if client.id == '1'][0]
        session.select_client(client)
        self.assertEqual('/client/1/', history[-1].path)

    def test_login_interactive(self, m):
        personal_question = u"¿Cuántos baños tenia la casa de mis padres?"
        m.post('/login/', json={
            'status': 'interaction_required',
            "context": personal_question,
            "field": "personal_question",
            'key': '123456',
        })
        session = self.client.banking.login(
            provider='test_provider',
            username='test_username',
            password='test_password',
        )
        self.assertEqual('interaction_required', session.get_status())
        self.assertEqual('123456', session.get_session_key())
        self.assertEqual(personal_question, session.get_interactive_context())

        m.post('/login/', json={
            'status': 'logged_in',
        })
        challenge_answer = 'test answer'
        session.finish_login(
            'test_provider', 'test_username', 'test_password', challenge_answer
        )
        request_body = parse_qs(m.last_request.text)
        self.assertEqual(request_body['personal_question'][0], challenge_answer)

    def test_get_accounts(self, m):
        m.get('/account/', json={
            "accounts": [
                {
                    "balance": 1234.95,
                    "branch": "02 - 18 De Julio",
                    "currency": "UYU",
                    "id": "hash1",
                    "name": "Cuenta total",
                    "number": "001234567890"
                },
                {
                    "balance": 53.96,
                    "branch": "61 - Ciudad Vieja",
                    "currency": "USD",
                    "id": "hash4",
                    "name": "Caja De Ahorro Atm",
                    "number": "004327567890"
                }
            ],
            "status": "success",
        })
        session_key = 'test_session_key'
        accounts = self.client.banking.get_accounts(session_key)
        self.assertEqual('/account/', m.last_request.path)
        self.assertEqual(session_key, m.last_request.qs['key'][0])
        self.assertEqual(2, len(accounts))
        self.assertEqual("Cuenta total", accounts[0].name)
        self.assertEqual("Caja De Ahorro Atm", accounts[1].name)

    def test_get_movements(self, m):
        m.get('/movement/', json={
            "movements": [
                {
                    "credit": "",
                    "date": "12/01/2019",
                    "debit": 3500,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.C. ",
                    "id": -890185180,
                    "reference": "000000005084"
                },
                {
                    "credit": "",
                    "date": "05/07/2019",
                    "debit": 16000,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.H Y ",
                    "id": 1024917397,
                    "reference": "000000002931"
                },
            ],
            "status": "success",
        })
        session_key = 'test_session_key'
        account_number = '001234567'
        currency_code = 'USD'
        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        movements = self.client.banking.get_movements(
            session_key, account_number, currency_code, date_start, date_end
        )
        qs = parse_qs(urlparse(m.last_request.url).query)
        self.assertEqual('/movement/', m.last_request.path)
        self.assertEqual(session_key, qs['key'][0])
        self.assertEqual(account_number, qs['account'][0])
        self.assertEqual(currency_code, qs['currency'][0])
        self.assertEqual('01/01/2019', qs['date_start'][0])
        self.assertEqual('01/12/2019', qs['date_end'][0])
        self.assertEqual(2, len(movements))
        self.assertEqual(datetime(2019, 1, 12), movements[0].date)
        self.assertEqual(datetime(2019, 7, 5), movements[1].date)

    def test_get_credit_cards(self, m):
        m.get('/credit-card/', json={
            "credit_cards": [
                {
                    "balance_dollar": 67.89,
                    "balance_local": 12345.42,
                    "close_date": "04/11/2019",
                    "due_date": "20/11/2019",
                    "id": "EcebS0rIZ5NdJNzS4XHmuOnHvSsI72TSA3j/8drzYYHtW1sQbpz5Hc",
                    "name": "Vi Int Sumaclub Plus",
                    "number": "770012345678"
                }
            ],
            "status": "success",
        })
        session_key = 'test_session_key'
        cards = self.client.banking.get_credit_cards(session_key)
        self.assertEqual('/credit-card/', m.last_request.path)
        self.assertEqual(session_key, m.last_request.qs['key'][0])
        self.assertEqual(1, len(cards))
        self.assertEqual("Vi Int Sumaclub Plus", cards[0].name)
        self.assertEqual("770012345678", cards[0].number)
        self.assertEqual(datetime(2019, 11, 20), cards[0].due_date)

    def test_get_credit_card_movements(self, m):
        m.get('/credit-card/1234567/movements', json={
            "movements": [
                {
                    "credit": "",
                    "date": "12/01/2019",
                    "debit": 3500,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.C. ",
                    "id": -890185180,
                    "reference": "000000005084"
                },
                {
                    "credit": "",
                    "date": "05/07/2019",
                    "debit": 16000,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.H Y ",
                    "id": 1024917397,
                    "reference": "000000002931"
                },
            ],
            "status": "success",
        })
        session_key = 'test_session_key'
        card_number = '1234567'
        currency_code = 'USD'
        date_start = datetime(2019, 1, 1)
        date_end = datetime(2019, 12, 1)
        movements = self.client.banking.get_credit_card_movements(
            session_key, card_number, currency_code, date_start, date_end
        )
        qs = parse_qs(urlparse(m.last_request.url).query)
        self.assertEqual('/credit-card/1234567/movements', m.last_request.path)
        self.assertEqual(session_key, qs['key'][0])
        self.assertEqual(currency_code, qs['currency'][0])
        self.assertEqual('01/01/2019', qs['date_start'][0])
        self.assertEqual('01/12/2019', qs['date_end'][0])
        self.assertEqual(2, len(movements))
        self.assertEqual(datetime(2019, 1, 12), movements[0].date)
        self.assertEqual(datetime(2019, 7, 5), movements[1].date)

    def test_get_providers(self, m):
        m.get('/provider/', json={
            "providers": [
                {
                    "code": "test",
                    "country": "UY",
                    "name": "Test Provider"
                }
            ],
            "status": "success",
        })
        providers = self.client.banking.get_providers()
        self.assertEqual(1, len(providers))
        self.assertEqual('test', providers[0].code)
        self.assertEqual('UY', providers[0].country)
        self.assertEqual('Test Provider', providers[0].name)

    def test_get_provider_detail(self, m):
        m.get('/provider/test/', json={
            "provider": {
                "auth_fields": [
                    {
                        "interactive": False,
                        "name": "username",
                        "type": "text"
                    },
                    {
                        "interactive": False,
                        "name": "password",
                        "type": "password"
                    }
                ],
                "country": "UY",
                "name": "test provider"
            },
            "status": "success",
        })
        provider = self.client.banking.get_provider_detail('test')
        self.assertEqual('UY', provider.country)
        self.assertEqual('test provider', provider.name)
        self.assertEqual(2, len(provider.auth_fields))

    def test_provider_doesnt_exist(self, m):
        m.get('/provider/invalid/', status_code=404, json={
            "status": "provider_doesnt_exist",
        })
        with self.assertRaises(exceptions.NotFoundError):
            self.client.banking.get_provider_detail('invalid')
