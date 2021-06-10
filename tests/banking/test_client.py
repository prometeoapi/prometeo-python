# -*- coding: utf-8 -*-
from datetime import datetime

from six.moves.urllib.parse import parse_qs, urlparse
import requests_mock

from prometeo import exceptions
from prometeo.banking import exceptions as banking_exceptions
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

    def test_generic_login_error(self, m):
        m.post('/login/', status_code=200, json={
            'status': 'error',
            'message': 'An error has ocurred.',
        })
        with self.assertRaises(banking_exceptions.BankingClientError):
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
        session_key = '123456'
        personal_question = u"¿Cuántos baños tenia la casa de mis padres?"
        m.post('/login/', json={
            'status': 'interaction_required',
            "context": personal_question,
            "field": "personal_question",
            'key': session_key,
        })
        session = self.client.banking.login(
            provider='test_provider',
            username='test_username',
            password='test_password',
        )
        self.assertEqual('interaction_required', session.get_status())
        self.assertEqual(session_key, session.get_session_key())
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
        self.assertEqual(m.last_request.qs['key'][0], session_key)

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
                    "reference": "000000005084",
                    "extra_data": None
                },
                {
                    "credit": "",
                    "date": "05/07/2019",
                    "debit": 16000,
                    "detail": "RETIRO EFECTIVO CAJERO AUTOMATICO J.H Y ",
                    "id": 1024917397,
                    "reference": "000000002931",
                    "extra_data": None
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

    def test_logout(self, m):
        m.get('/logout/', json={'status': 'logged_out'})
        session_key = 'test_session_key'
        self.client.banking.logout(session_key)
        qs = parse_qs(urlparse(m.last_request.url).query)
        self.assertEqual('/logout/', m.last_request.path)
        self.assertEqual(session_key, qs['key'][0])

    def test_preprocess_transfer(self, m):
        m.post('/transfer/preprocess', json={
            "result": {
                "approved": True,
                "authorization_devices": [
                    {
                        "data": ["F-4", "B-2", "G-7"],
                        "type": "cardCode"
                    },
                    {
                        "data": None,
                        "type": "pin"
                    }
                ],
                "message": None,
                "request_id": "0b7d6b32d1be4c11bde21e7ddc08cc36"
            },
            "status": "success"
        })
        session_key = 'test_session_key'
        origin_account = '002206345988'
        destination_institution = '0'
        destination_account = '001002363321'
        currency = 'UYU'
        amount = '1.3'
        concept = 'descripcion de transferencia'
        destination_owner_name = 'John Doe'
        branch = '62'
        preprocess = self.client.banking.preprocess_transfer(
            session_key, origin_account, destination_institution,
            destination_account, currency, amount, concept,
            destination_owner_name, branch
        )
        self.assertEqual(True, preprocess.approved)
        self.assertEqual(3, len(preprocess.authorization_devices[0]['data']))
        self.assertEqual('cardCode', preprocess.authorization_devices[0]['type'])
        self.assertEqual('0b7d6b32d1be4c11bde21e7ddc08cc36', preprocess.request_id)
        self.assertEqual(None, preprocess.message)

    def test_confirm_transfer(self, m):
        m.post('/transfer/confirm', json={
            "status": "success",
            "transfer": {
                "message": "Transferencia confirmada con exito",
                "success": True
            }
        })
        session_key = 'test_session_key'
        request_id = '0b7d6b32d1be4c11bde21e7ddc08cc36'
        authorization_type = 'cardCode'
        authorization_data = '1, 2, 3'
        confirmation = self.client.banking.confirm_transfer(
            session_key, request_id, authorization_type, authorization_data
        )
        self.assertEqual(True, confirmation.success)
        self.assertNotEqual(None, confirmation.message)

    def test_list_transfer_institutions(self, m):
        m.get('/transfer/destinations', json={
            "destinations": [
                {
                    "id": 0,
                    "name": "SANTANDER"
                },
                {
                    "id": 1,
                    "name": "B.R.O.U."
                },
                {
                    "id": 91,
                    "name": "B.H.U."
                },
                {
                    "id": 110,
                    "name": "BANDES"
                }
            ],
            "status": "success"
        })
        session_key = 'test_session_key'
        institutions = self.client.banking.list_transfer_institutions(session_key)
        self.assertNotEqual(0, len(institutions))

    def test_invalid_session_key(self, m):
        m.get('/account/', json={
            "message": "Invalid key",
            "status": "error"
        })
        with self.assertRaises(exceptions.InvalidSessionKeyError):
            self.client.banking.get_accounts('invalid_session_key')

    def test_generic_client_error(self, m):
        m.get('/account/', json={
            "message": "Some generic error",
            "status": "error"
        })
        with self.assertRaises(banking_exceptions.BankingClientError):
            self.client.banking.get_accounts('invalid_session_key')
