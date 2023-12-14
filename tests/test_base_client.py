from .base_test_case import BaseTestCase
import respx

from prometeo import base_client, exceptions


class TestCase(BaseTestCase):
    def setUp(self):
        self.sandbox_url = "https://test.example.com"
        self.prod_url = "https://prod.example.com"
        base_client.BaseClient.ENVIRONMENTS = {
            "sandbox": self.sandbox_url,
            "production": self.prod_url,
        }
        self.api_key = "test_api_key"
        self.environment = "sandbox"
        self.client = base_client.BaseClient(self.api_key, self.environment)

    @respx.mock
    async def test_api_key(self):
        self.mock_get_request(respx, "/test/", json={})
        await self.client.call_api("GET", "/test/")
        request = respx.calls[0].request
        self.assertIn("X-API-Key", request.headers)
        self.assertEqual(self.api_key, request.headers["X-API-Key"])

    @respx.mock
    async def test_envs(self):
        self.mock_get_request(respx, "/test/", json={})
        history = respx.calls

        test_client = base_client.BaseClient(self.api_key, "sandbox")
        await test_client.call_api("GET", "/test/")
        self.assertIn(self.sandbox_url, str(history[-1].request.url))

        prod_client = base_client.BaseClient(self.api_key, "production")
        await prod_client.call_api("GET", "/test/")
        self.assertIn(self.prod_url, str(history[-1].request.url))

    @respx.mock
    def test_invalid_env(self):
        with self.assertRaises(exceptions.ClientError):
            base_client.BaseClient(self.api_key, "invalid")

    @respx.mock
    async def test_unauthorized(self):
        self.mock_get_request(
            respx,
            "/test/",
            status_code=401,
            json={
                "status": "error",
                "message": "Missing API key",
            },
        )
        with self.assertRaises(exceptions.UnauthorizedError):
            await self.client.call_api("GET", "/test/")

    @respx.mock
    async def test_forbidden(self):
        self.mock_get_request(
            respx,
            "/test/",
            status_code=403,
            json={
                "status": "error",
                "message": "Key not found",
            },
        )
        with self.assertRaises(exceptions.ForbiddenError):
            await self.client.call_api("GET", "/test/")

    @respx.mock
    async def test_missing_credentials(self):
        self.mock_post_request(
            respx,
            "/login/",
            status_code=400,
            json={
                "status": "missing_credentials",
                "message": "missing credentials",
            },
        )
        with self.assertRaises(exceptions.BadRequestError):
            await self.client.call_api("POST", "/login/")

    @respx.mock
    async def test_wrong_parameters(self):
        self.mock_get_request(
            respx,
            "/test/",
            status_code=400,
            json={
                "status": "missing_params",
                "message": "missing parameters",
            },
        )
        with self.assertRaises(exceptions.BadRequestError):
            await self.client.call_api("GET", "/test/")

    @respx.mock
    async def test_404_without_json(self):
        self.mock_get_request(respx, "/invalid/", status_code=404, text="Not found.")
        with self.assertRaises(exceptions.NotFoundError):
            await self.client.call_api("GET", "/invalid/")

    @respx.mock
    async def test_internal_error(self):
        error_message = "Server got itself in trouble."
        self.mock_get_request(respx, "/test/", status_code=500, text=error_message)
        with self.assertRaises(exceptions.InternalAPIError) as cm:
            await self.client.call_api("GET", "/test/")

        self.assertEqual(error_message, cm.exception.message)

    @respx.mock
    async def test_provider_unavailable(self):
        self.mock_get_request(
            respx,
            "/test/",
            status_code=503,
            json={
                "status": "provider_unavailable",
                "message": "Provider returned 500 response.",
            },
        )
        with self.assertRaises(exceptions.ProviderUnavailableError):
            await self.client.call_api("GET", "/test/")

    @respx.mock
    async def test_raw_response(self):
        self.mock_get_request(
            respx,
            "/test/",
            json={
                "name": "test",
                "aliases": ["alias_test"],
                "country": "UY",
                "endpoints_status": None,
                "account_type": [
                    {
                        "name": "pers",
                        "label_es": "Cuenta Personal",
                        "label_en": "Personal Account",
                    },
                    {
                        "name": "corp",
                        "label_es": "Cuenta Corporativa",
                        "label_en": "Corporate Account",
                    },
                ],
            },
        )
        client = base_client.BaseClient(self.api_key, self.environment, True)
        respose = await client.call_api("GET", "/test/")
        self.assertEqual(200, respose.status_code)
        self.assertEqual("test", respose.json()["name"])
        self.assertEqual("UY", respose.json()["country"])
