import requests_mock

from prometeo import exceptions
from prometeo.account_validation import exceptions as av_exceptions
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestClient(BaseTestCase):
    def test_invalid_parameters(self, m):
        self.mock_post_request(m, "/validate-account/", "invalid_parameters")

        with self.assertRaises(exceptions.InvalidParameterError) as e:
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )

        self.assertIn("account_number", e.exception.params)

    def test_invalid_parameters_many_errors(self, m):
        self.mock_post_request(m, "/validate-account/", "invalid_parameters_many")

        with self.assertRaises(exceptions.InvalidParameterError) as e:
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )

        self.assertIn("account_number", e.exception.params)
        self.assertIn("Some description indicating error", e.exception.message)

    def test_invalid_account(self, m):
        self.mock_post_request(m, "/validate-account/", "invalid_account")

        with self.assertRaises(av_exceptions.InvalidAccountError):
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )

    def test_validate_accounts(self, m):
        self.mock_post_request(m, "/validate-account/", "valid_account_br")
        data = self.client.account_validation.validate(
            account_number="***",
            country_code="BR",
        )
        self.assertEqual(data.beneficiary_name, "JOÃO DAS NEVES")

        self.mock_post_request(m, "/validate-account/", "valid_account_mx")
        data = self.client.account_validation.validate(
            account_number="***",
            country_code="MX",
        )
        self.assertEqual(data.beneficiary_name, "CRUZ ROJA MEXICANA")

        self.mock_post_request(m, "/validate-account/", "valid_account_pe")
        data = self.client.account_validation.validate(
            account_number="***",
            country_code="PE",
        )
        self.assertEqual(data.beneficiary_name, "VILLANCA ROSALES ANDREA CLAUDIA")

        self.mock_post_request(m, "/validate-account/", "valid_account_uy")
        data = self.client.account_validation.validate(
            account_number="***",
            country_code="UY",
        )
        self.assertEqual(data.beneficiary_name, "DANI*** DEC*** COL**")

    def test_communication_error(self, m):
        with self.assertRaises(av_exceptions.CommunicationError):
            self.mock_post_request(m, "/validate-account/", "communication_error")
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )

    def test_method_not_available_error(self, m):
        with self.assertRaises(av_exceptions.MethodNotAvailableError):
            self.mock_post_request(
                m, "/validate-account/", "method_not_available_error"
            )
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )

    def test_bank_provider_not_available_error(self, m):
        with self.assertRaises(av_exceptions.BankProviderNotAvailableError):
            self.mock_post_request(m, "/validate-account/", "bank_not_available_error")
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )

    def test_country_not_available_error(self, m):
        with self.assertRaises(av_exceptions.CountryNotAvailableError):
            self.mock_post_request(
                m, "/validate-account/", "country_not_available_error"
            )
            self.client.account_validation.validate(
                account_number="9999",
                country_code="BR",
                document_number="58.547.642/0001-95",
                branch_code="00001",
                bank_code="999",
                account_type="CHECKING",
            )
