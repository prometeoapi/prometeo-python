import unittest

import requests_mock

from prometeo import base_client, exceptions


@requests_mock.Mocker()
class TestCase(unittest.TestCase):

    def setUp(self):
        self.testing_url = 'https://test.example.com'
        self.prod_url = 'https://prod.example.com'
        base_client.BaseClient.ENVIRONMENTS = {
            'testing': self.testing_url,
            'production': self.prod_url,
        }
        self.api_key = 'test_api_key'
        self.environment = 'testing'
        self.client = base_client.BaseClient(self.api_key, self.environment)

    def test_api_key(self, m):
        m.get('/test/', json={})
        self.client.call_api('GET', '/test/')
        request = m.request_history[0]
        self.assertIn('X-API-Key', request.headers)
        self.assertEqual(self.api_key, request.headers['X-API-Key'])

    def test_envs(self, m):
        m.get('/test/', json={})
        history = m.request_history

        test_client = base_client.BaseClient(self.api_key, 'testing')
        test_client.call_api('GET', '/test/')
        self.assertIn(self.testing_url, history[-1].url)

        prod_client = base_client.BaseClient(self.api_key, 'production')
        prod_client.call_api('GET', '/test/')
        self.assertIn(self.prod_url, history[-1].url)

    def test_invalid_env(self, m):
        with self.assertRaises(exceptions.ClientError):
            base_client.BaseClient(self.api_key, 'invalid')

    def test_unauthorized(self, m):
        m.get('/test/', status_code=401, json={
            "status": "error",
            "message": "Missing API key",
        })
        with self.assertRaises(exceptions.UnauthorizedError):
            self.client.call_api('GET', '/test/')

    def test_forbidden(self, m):
        m.get('/test/', status_code=403, json={
            "status": "error",
            "message": "Key not found",
        })
        with self.assertRaises(exceptions.ForbiddenError):
            self.client.call_api('GET', '/test/')

    def test_missing_credentials(self, m):
        m.post('/login/', status_code=400, json={
            "status": "missing_credentials",
            "message": "missing credentials",
        })
        with self.assertRaises(exceptions.BadRequestError):
            self.client.call_api('POST', '/login/')

    def test_wrong_parameters(self, m):
        m.get('/test/', status_code=400, json={
            "status": "missing_params",
            "message": "missing parameters",
        })
        with self.assertRaises(exceptions.BadRequestError):
            self.client.call_api('GET', '/test/')

    def test_404_without_json(self, m):
        m.get('/invalid/', status_code=404, text='Not found.')
        with self.assertRaises(exceptions.NotFoundError):
            self.client.call_api('GET', '/invalid/')

    def test_internal_error(self, m):
        error_message = 'Server got itself in trouble.'
        m.get('/test/', status_code=500, text=error_message)
        with self.assertRaises(exceptions.InternalAPIError) as cm:
            self.client.call_api('GET', '/test/')

        self.assertEqual(error_message, cm.exception.message)

    def test_provider_unavailable(self, m):
        m.get('/test/', status_code=503, json={
            "status": "provider_unavailable",
            "message": "Provider returned 500 response.",
        })
        with self.assertRaises(exceptions.ProviderUnavailableError):
            self.client.call_api('GET', '/test/')
